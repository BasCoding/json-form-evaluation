# json-form-evaluation
The purpose of this directory is to evaluate the correctness of a predicted JSON form to a ground truth JSON form.

A JSON form is loaded in as a dictionary. For every field in the form is evaluated if the actual value is equal to the predicted value. For now it only supports a 100% match. The evaluation can handle JSON that contain multiple arrays or objects.

## Usage
The evaluator can compare dictionaries, JSON files or directories containing JSON files. The following example shows how to use the evaluator when the JSON files are stored in directories. The `data/actual` path contains the JSON files with the ground truth, the `data/predicted` path contains the JSON files with predicted values. Note that the files that are compared must have the same name (e.g. `data/actual/0.json` and `data/predicted/0.json` are compared).

```
from json_form_evaluation.evaluate import JsonFormEvaluator
evaluator = JsonFormEvaluator()
evaluator.compare_from_dirs("data/actual","data/predicted")
print(evaluator.calculate_score("accuracy"))
```