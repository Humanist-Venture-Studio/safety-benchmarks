"""Train-only mixed verdict baseline/refit, selected after Q6_K export rounding.

Adapted from the supplied tune.py and PR #8's tune_chat.py objective. Each task
contributes half the loss; single unsafe labels marginalize Unsafe/Controversial.
"""
import argparse
import json
from pathlib import Path
import shutil

from gguf import GGUFReader, GGMLQuantizationType, dequantize
import numpy as np
from scipy.optimize import minimize
from scipy.special import softmax
from scipy.linalg import solve_triangular

from tune import q6_rows
from v3_export import patch_template
import v3_protocol as p


def fit(root, prepared, out, baseline, model=None, penalties=(.004, .0004, .00004), drifts=(.02, .2),
        maxiter=400, precondition=False):
    out.mkdir(parents=True)
    token_data = json.loads((prepared / 'tokens.json').read_text())
    if token_data['protocol_sha256'] != p.sha(p.__file__) or token_data['template_sha256'] != p.sha(p.TEMPLATE):
        raise ValueError('Prepared contract differs')
    tokens = token_data['items']; ids = token_data['ids']
    all_items, _ = p.load(root)
    lookup = {(it['source'], it['index']): it for it in all_items}
    items = [lookup[it['source'], it['index']] for it in tokens]
    features = np.load(prepared / 'features.npz')
    vectors = features['vectors'].astype(np.float64)
    anchors = features['anchors'].astype(np.float64)
    train = np.array([it['split'] == 'train' for it in items])
    val = ~train
    if any(it['split'] not in ('train', 'validation') for it in items):
        raise ValueError('Unexpected held-out item')
    single = np.array([it['source'] == 'single' for it in items])[train]
    masks = np.array([it['mask'] for it in items], dtype=np.float64)[train]
    source = json.loads((prepared / 'source.json').read_text())
    model = model or Path(source['path'])
    if source['sha256'] != p.sha(model):
        raise ValueError('Feature/model mismatch')
    reader = GGUFReader(model)
    head = next(t for t in reader.tensors if t.name == 'output.weight')
    if head.tensor_type != GGMLQuantizationType.Q6_K:
        raise ValueError('Expected Q6_K output')
    weights = dequantize(head.data[ids], head.tensor_type).astype(np.float64)
    scale = np.sqrt(vectors[train].std(0).clip(.08))
    x, z = vectors[train] / scale, anchors / scale
    base = vectors[train] @ weights.T
    row_weights = np.where(single, .5 / single.sum(), .5 / (~single).sum())
    reference = json.loads(baseline.read_text())
    val_items = [it for it in items if it['split'] == 'validation']
    source_logits = vectors[val] @ weights.T
    source_votes = ['invalid' if bad else p.VERDICTS[j] for j, bad in zip(source_logits.argmax(-1), source_logits.max(-1) < features['other'][val])]
    source_scores = p.summary(val_items, source_votes)
    (out / 'source-validation.json').write_text(json.dumps(source_scores, indent=2) + '\n')
    print('Source validation by quantized logits', json.dumps(source_scores), flush=True)
    history, chosen = [], None
    if precondition:
        train_curvature = .25 * (x.T @ (row_weights[:, None] * x))
        anchor_curvature = 2 * (z.T @ z) / len(z)
    for penalty in penalties:
        for drift in drifts:
            # Invert a positive block-diagonal Hessian approximation. This is
            # only a change of optimization coordinates: the original loss,
            # task weights, L2 penalty and formatting drift are unchanged.
            right = None
            fx, fz = x, z
            if precondition:
                factor = np.linalg.cholesky(train_curvature + drift * anchor_curvature + penalty * np.eye(x.shape[1]))
                right = solve_triangular(factor, np.eye(x.shape[1]), lower=True)
                fx, fz = x @ right.T, z @ right.T
            def objective(flat):
                latent = flat.reshape(3, -1)
                update = latent if right is None else latent @ right
                logits = base + fx @ latent.T
                prob = softmax(logits, axis=1)
                hit = (prob * masks).sum(1).clip(1e-300)
                anchor_delta = fz @ latent.T
                loss = -(row_weights * np.log(hit)).sum() + penalty / 2 * (update ** 2).sum() + drift * (anchor_delta ** 2).sum() / len(z)
                regularization_grad = penalty * update if right is None else penalty * update @ right.T
                grad = ((prob - prob * masks / hit[:, None]) * row_weights[:, None]).T @ fx + regularization_grad + 2 * drift * anchor_delta.T @ fz / len(z)
                return loss, grad.ravel()
            result = minimize(objective, np.zeros(weights.size), jac=True, method='L-BFGS-B', options={'maxiter': maxiter})
            if not np.isfinite(result.fun) or not np.isfinite(result.x).all():
                raise ValueError('Nonfinite head optimizer result')
            update = result.x.reshape(3, -1)
            if right is not None:
                update = update @ right
            packed = q6_rows(weights + update / scale)
            rounded = dequantize(packed, head.tensor_type)
            logits = vectors[val] @ rounded.T
            picked = logits.argmax(-1)
            stray = logits.max(-1) < features['other'][val]
            votes = ['invalid' if bad else p.VERDICTS[j] for j, bad in zip(picked, stray)]
            report = p.summary(val_items, votes)
            av = anchors @ rounded.T
            was_verdict = np.isin(features['anchor_choice'], ids)
            now_verdict = av.max(-1) > features['anchor_other']
            choice = np.array(ids)[av.argmax(-1)]
            changed = int(((now_verdict & (choice != features['anchor_choice'])) | (~now_verdict & was_verdict)).sum())
            record = dict(penalty=penalty, drift=drift, preconditioned=precondition, max_iterations=maxiter,
                          objective=float(result.fun), gradient_inf_norm=float(np.abs(result.jac).max()), iterations=int(result.nit),
                          optimizer_success=bool(result.success), optimizer_message=str(result.message),
                          validation=report, format_anchors_changed=changed, selection_key=p.selection(report, reference))
            history.append(record)
            print(json.dumps(record), flush=True)
            # Formatting must survive before a numerical accuracy gain matters.
            key = (-changed, *p.selection(report, reference))
            if chosen is None or key > chosen[0]:
                chosen = key, record, packed.copy(), votes
    path = out / 'candidate.gguf'
    shutil.copyfile(model, path)
    with path.open('r+b') as f:
        for token, row in zip(ids, chosen[2]):
            f.seek(int(head.data_offset) + token * head.data.strides[0]); f.write(row.tobytes())
    patch_template(path)
    (out / 'Modelfile').write_text(p.definition('./candidate.gguf'))
    (out / 'history.json').write_text(json.dumps(history, indent=2) + '\n')
    (out / 'selected.json').write_text(json.dumps(chosen[1] | dict(gguf_sha256=p.sha(path), source_sha256=p.sha(model)), indent=2) + '\n')
    (out / 'validation-votes.json').write_text(json.dumps(chosen[3]) + '\n')
    print('Head ready:', path, flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path.cwd())
    ap.add_argument('--prepared', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--baseline', required=True, type=Path)
    ap.add_argument('--model', type=Path)
    ap.add_argument('--maxiter', type=int, default=400)
    ap.add_argument('--precondition', action='store_true')
    a = ap.parse_args()
    fit(a.root, a.prepared, a.out, a.baseline, a.model, maxiter=a.maxiter, precondition=a.precondition)
