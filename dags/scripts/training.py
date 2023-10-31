import pandas as pd
from sklearn import linear_model
from sklearn.linear_model import SGDRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import KFold
import argparse
import os

parser = argparse.ArgumentParser(
                    prog='data_intake',
                    description='Intakes data',
                    epilog='Data')
parser.add_argument('--filename')
parser.add_argument('--upstream_task')
args = parser.parse_args()

file = f"/opt/airflow/data_files/{args.upstream_task}/{args.filename}"
# Load the data
df = pd.read_csv(file)

y = df["MINLAPTIME"]
X = df.drop("MINLAPTIME", axis=1)

kf = KFold(n_splits=3)
reg = make_pipeline(StandardScaler(), SGDRegressor(max_iter=1000, tol=1e-3))

acc_score = []
for i, (train_index , test_index) in enumerate(kf.split(X)):
    X_train , X_test = X.iloc[train_index,:],X.iloc[test_index,:]
    y_train , y_test = y[train_index] , y[test_index]
    
    reg.fit(X_train,y_train)
    pred_values = reg.predict(X_test)
    
    acc = mean_squared_error(y_test, pred_values)
    r2 = r2_score(y_test, pred_values)
    results_df = list(zip(y_test, pred_values))
    print(results_df)
    acc_score.append((i, acc, r2))
    # print(list(zip(reg.coef_, reg.feature_names_in_)))

df = pd.DataFrame(acc_score, columns=['FOLD_NUM', 'R_SQUARED', 'ACCURACY_SCORE'])

task_id = os.environ['task_id']
output_path = f"/opt/airflow/data_files/{task_id}"
os.makedirs(output_path, exist_ok=True)

file_path = f"{output_path}/{args.filename}"
df.to_csv(file_path, index=False)