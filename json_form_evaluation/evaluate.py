import glob
import json
import logging
import os
import re

log = logging.getLogger("json_form_evaluation")


class JsonFormEvaluator:
    """A Evaluator for JSON forms"""

    def __init__(self):
        """
        Initialize the evaluator
        """
        self.evaluation = {}

    def calculate_score(self, metric: str):
        """
        Calculate the score for each JSON form field.

        Args
            metric: method used to calculate the score
        """
        if metric == "accuracy":
            score = {
                k: v["Correct"] / (v["Correct"] + v["Incorrect"])
                for k, v in self.evaluation.items()
            }
        else:
            raise Exception(
                f"Unsupported metric '{metric}', please provid a valid one."
            )
        return score

    def compare_forms(self, d_actual: dict, d_predicted: dict, prefix: str = ""):
        """
        Compare forms by traversing through dicts and lists recursively to handle nested fields.
        Results in a metrics that contain number of correct values.

        Args
            d_actual: Ground truth JSON form
            d_predicted: Predicted JSON form
            prefix: Prefix used for recursion if JSON form is multiple levels deep
        """
        if self.evaluation is None:
            self.evaluation = {}
        for key in d_actual.keys():
            if isinstance(d_actual[key], dict):
                # if dictionary recursively add metrics for each of the keys
                self.compare_forms(
                    d_actual[key], d_predicted.get(key, {}), prefix + key + "."
                )
            elif isinstance(d_actual[key], list):
                len_actual = len(d_actual[key])
                # ensure we can compare actual to predicted
                predicted_list = d_predicted.get(key)
                if predicted_list is None:
                    predicted_list = [{}] * len_actual
                len_pred = len(predicted_list)
                if len_actual > len_pred:
                    for i in range(len_actual - len_pred):
                        predicted_list.append({})

                # if list recursively add metrics for each of the keys for each of the dictionaries in the list
                for i in range(len_actual):
                    if isinstance(d_actual[key][i], dict):
                        predicted_value = predicted_list[i]
                        self.compare_forms(
                            d_actual[key][i], predicted_value, prefix + key + "."
                        )
                    else:
                        logger.warning(
                            f"Unexpected field format in actual form: {key}, {i}, {d_actual[key][i]}"
                        )
            else:
                full_key = prefix + key
                full_key = re.sub(
                    "\.\d+\.", ".", full_key
                )  # Remove the index from the field name
                actual_value = d_actual[key]
                predicted_value = d_predicted.get(key, None)
                if full_key not in self.evaluation:
                    self.evaluation[full_key] = {
                        "Correct": 0,
                        "Incorrect": 0,
                        "TN": 0,
                        "FP": 0,
                        "FN": 0,
                        "TP": 0,
                    }

                if predicted_value == actual_value:
                    self.evaluation[full_key]["Correct"] += 1
                else:
                    self.evaluation[full_key]["Incorrect"] += 1

                if actual_value == None and predicted_value == None:
                    self.evaluation[full_key]["TN"] += 1
                elif actual_value == None and predicted_value != None:
                    self.evaluation[full_key]["FP"] += 1
                elif actual_value != None and predicted_value == None:
                    self.evaluation[full_key]["FN"] += 1
                elif actual_value != None and predicted_value != None:
                    self.evaluation[full_key]["TP"] += 1

    def compare_forms_from_path(self, actual_path: str, pred_path: str):
        """
        Compare two JSON forms stored in a path

        Args
            actual_path: file path containing actual JSON
            pred_path: file path containing predicted JSON
        """
        if actual_path.endswith(".json") and pred_path.endswith(".json"):
            with open(actual_path, "r") as f:
                d_actual = json.load(f)

            with open(pred_path, "r") as f:
                d_pred = json.load(f)

            self.compare_forms(d_actual, d_pred)
        else:
            raise Exception(
                f"Incorrect paths '{actual_path}' and '{pred_path}'. We only support JSON files."
            )

    def compare_from_dirs(self, actual_dir: str, pred_dir: str):
        """
        Compare all JSON forms in the provided directories.
        We assume the files to compare have the same filename.

        Args
            actual_dir: path containing all actual JSON forms
            pred_dir: path containing all predicted json forms
        """
        actual_files = glob.glob(os.path.join(actual_dir, "*.json"))
        for actual_file in actual_files:
            pred_file = actual_file.replace(actual_dir, pred_dir)
            self.compare_forms_from_path(actual_file, pred_file)
