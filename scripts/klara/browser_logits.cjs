const path = require("node:path");
const fs = require("node:fs");
const { AutoTokenizer, AutoModelForSequenceClassification, env } = require("@huggingface/transformers");

async function main() {
  env.allowRemoteModels = false;
  const directory = process.argv[2];
  const tokenizer = await AutoTokenizer.from_pretrained(directory);
  const dtype = fs.existsSync(path.join(directory, "onnx", "model_fp16.onnx")) ? "fp16" : "q8";
  const model = await AutoModelForSequenceClassification.from_pretrained(directory, {dtype, device: "cpu"});
  const scores = [];
  for (const text of JSON.parse(fs.readFileSync(0, "utf8"))) {
    const {logits} = await model(tokenizer(text));
    scores.push(Array.from(logits.data));
  }
  console.log(JSON.stringify(scores));
  await model.dispose();
}
main().catch(error => { console.error(error); process.exitCode = 1; });
