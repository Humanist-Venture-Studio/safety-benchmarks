const path = require("node:path");
const fs = require("node:fs");
const { AutoTokenizer, AutoModelForSequenceClassification, PreTrainedModel, env } = require("@huggingface/transformers");

async function main() {
  env.allowRemoteModels = false;
  const directory = process.argv[2];
  const tokenizer = await AutoTokenizer.from_pretrained(directory);
  const dtype = fs.existsSync(path.join(directory, "onnx", "model_fp16.onnx")) ? "fp16" : "q8";
  const config = JSON.parse(fs.readFileSync(path.join(directory, "config.json"), "utf8"));
  const Model = config.klara_verdict_ids ? PreTrainedModel : AutoModelForSequenceClassification;
  const model = await Model.from_pretrained(directory, {dtype, device: "cpu"});
  const scores = [];
  for (const text of JSON.parse(fs.readFileSync(0, "utf8"))) {
    const {logits} = await model(tokenizer(text));
    scores.push(Array.from(logits.data));
  }
  console.log(JSON.stringify(scores));
  await model.dispose();
}
main().catch(error => { console.error(error); process.exitCode = 1; });
