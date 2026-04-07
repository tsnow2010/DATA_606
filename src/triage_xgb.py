import pandas as pd
# ML Packages
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import roc_auc_score
import xgboost as xgb


def train_xgb_booster(X_train, X_val, y_train, y_val, num_boost_round):

  # Assign splits to XGBoost DMatrix
  dtrain = xgb.DMatrix(X_train, label=y_train, enable_categorical=True)
  dval = xgb.DMatrix(X_val,label=y_val, enable_categorical=True)


  # Train the XGBoost model
  params = {
      "objective": "binary:logistic",
      "eval_metric": "auc",
      "tree_method": "hist"
  }

  evals = [(dtrain, "train"), (dval, "val")]

  model = xgb.train(
      params,
      dtrain,
      num_boost_round=num_boost_round,
      evals=evals,
      early_stopping_rounds=10
  )

  return model

def make_xgb_predictions(model, X_test, y_test):
  dtest  = xgb.DMatrix(X_test,  label=y_test, enable_categorical=True)
  preds = model.predict(dtest)

  # Print metrics
  best_auc = roc_auc_score(y_test, preds)
  print("AUC:", best_auc)

  y_pred_labels = (preds > 0.5).astype(int)

  print("Accuracy:", accuracy_score(y_test, y_pred_labels))
  print("Precision:", precision_score(y_test, y_pred_labels))
  print("Recall:", recall_score(y_test, y_pred_labels))
  print("F1 Score:", f1_score(y_test, y_pred_labels))

  return best_auc # consider returning dict of results

def get_importances(model):

  # Extract scores from Booster (model)
  scores = model.get_score(importance_type='gain')

  # Feature importances
  feat_imp = (
      pd.Series(scores)
      .sort_values(ascending=False)
      .rename("gain_importance")
  )

  # Print and return all features by descending importance
  print(feat_imp)
  print(feat_imp.shape)
  return feat_imp

def rfe_xgboost_booster(X_train, X_val, X_test, y_train, y_val, y_test, importances, best_auc, elimination_log, max_loss,min_features=100):
  
  new_importances = importances.copy()

  X_train_new = X_train.copy()
  X_val_new = X_val.copy()
  X_test_new = X_test.copy()
  y_train_new = y_train.copy()
  y_val_new = y_val.copy()
  y_test_new = y_test.copy()

  # Starting new log.
  if elimination_log is None:
    print("Starting new log.")
    elimination_log = [["None", best_auc, 0]]

  # Resuming from previous RFE log.
  else:
    print("Resuming log.")
    for feature_entry in elimination_log:
      if feature_entry[0] != "None": # try using len() to skip first element
        feature = feature_entry[0] 
        print(f'Dropping {feature}')
        # Drop feature from importances
        print(new_importances.shape)
        new_importances.drop(feature, inplace=True, errors='ignore')
        # Drop from feature from dataset
        print(X_train_new.shape)
        X_train_new.drop(feature, axis=1, inplace=True, errors='ignore')
        print(X_val_new.shape)
        X_val_new.drop(feature, axis=1, inplace=True, errors='ignore')
        print(X_test_new.shape)
        X_test_new.drop(feature, axis=1, inplace=True, errors='ignore')
    

  # Reverse list of importances in ascending order
  reverse_importances = new_importances.sort_values(ascending=True)

  continuing = True

  while continuing:
    print(f"Number of Features (before elimination): {reverse_importances.shape[0]}")
    # Identify least important feature and drop from datasets
    least_important = reverse_importances.index[0]
    reverse_importances.drop(least_important, inplace=True)
    X_train_new.drop(least_important, axis=1, inplace=True)
    X_val_new.drop(least_important, axis=1, inplace=True)
    X_test_new.drop(least_important, axis=1, inplace=True)

    # Train new model
    print(f"\nTrying removal: {least_important}")
    print(f"Number of Features (after elimination): {reverse_importances.shape[0]}")

    # Retrain
    model_new = train_xgb_booster(X_train_new, X_val_new, y_train, y_val, 128)
    auc_new = make_xgb_predictions(model_new, X_test_new, y_test)
    difference_auc = (best_auc - auc_new)

    print(f"\nAUC after removal: {auc_new:.4f}")

    # Accept or stop
    if (difference_auc >= max_loss) or \
     (reverse_importances.shape[0] == min_features) or \
      (reverse_importances.shape[0] == 1):

      print("Stopping RFE cycle...")
      elimination_log.append((least_important, auc_new, difference_auc))
      continuing = False
      
      print('Saving log...')
      write_log(elimination_log)
      
      print('Saving model...')
      model.save_model("model.json")

    else:
      elimination_log.append([least_important, auc_new, difference_auc])
      print(f"Removed: {least_important}\nAUC Difference: {difference_auc:4f}")


def write_log(log):
  with open (f"log.csv", "w") as file:
      file.write('Feature Removed,New AUC,AUC Difference\n')
  with open (f"log.csv", "a") as file:
    for entry in log:
      feature, auc, diff = entry
      print(f"Feature removed: {str(feature)}")
      print(f"New AUC: {float(auc):.4f}")
      print(f"AUC Difference: {float(diff):.4f}")
      print("---")
      file.write(f'{str(feature)},{float(auc):.4f},{float(diff):.4f}\n')

def read_log(log):
  elimination_log = []
  with open (log, "r") as file:
    next(file)
    for line in file:
      line_list = line.replace("\n", "").split(',')
      line_list[1] = float(line_list[1])
      line_list[2] = float(line_list[2])
      elimination_log.append(line_list)
  return elimination_log


# Returns discharge prediction based on model
def predict_discharge(data:pd.DataFrame):
  dsample = xgb.DMatrix(data, enable_categorical=True)
  pred = model.predict(dsample)
  if pred > 0.5:
    disp = True # discharged
    print("discharged")
  else:
    disp = False # admitted
    print("admitted")
  return disp
