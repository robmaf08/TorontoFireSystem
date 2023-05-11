import pandas as pd
import pickle
import numpy as np
import os

import sklearn.metrics
from sklearn.model_selection import cross_val_score, KFold
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_log_error
from sklearn.preprocessing import OrdinalEncoder

ESTIMATOR_PATH = "./supervised_learning/gbr_model.pkl"


class Estimator:
    gbr = None

    X = []
    y = []
    ordinal_encoder = None
    scaler = None

    X_train, X_test, y_train, y_test = [], [], [], []
    df = []

    def __init__(self):
        if os.path.exists(ESTIMATOR_PATH) is False:
            self.create_model()
        else:
            self.load_model()

    def create_model(self):
        # Load dataset
        self.df = pd.read_csv('./datasets/fire_knowledge.csv')

        # Create an instance of Ordinal Encoder.
        self.ordinal_encoder = OrdinalEncoder()

        # Create a list of all the categorical features
        cols = ['Area_of_Origin', 'Business_Impact', 'Extent_Of_Fire',
                'Fire_Alarm_System_Impact_on_Evacuation',
                'Fire_Alarm_System_Operation', 'Fire_Alarm_System_Presence',
                'Ignition_Source', 'Material_First_Ignited',
                'Method_Of_Fire_Control', 'Possible_Cause', 'Property_Use',
                'Smoke_Alarm_at_Fire_Origin_Alarm_Failure',
                'Smoke_Alarm_at_Fire_Origin_Alarm_Type',
                'Status_of_Fire_On_Arrival']

        # Fit ordinal encoder and return encoded label
        self.df[cols] = self.ordinal_encoder.fit_transform(self.df[cols])
        estimated_dollar_loss_log = np.where(self.df['Estimated_Dollar_Loss'] != 0,
                                             np.log(self.df['Estimated_Dollar_Loss']), 0)
        self.df['Estimated_Dollar_Loss'] = estimated_dollar_loss_log

        df2 = self.df.drop(['Fire_Under_Control_Time',
                            'Fire_Alarm_System_Impact_on_Evacuation',
                            'Possible_Cause', 'Method_Of_Fire_Control', 'Civilian_Casualties',
                            'Count_of_Persons_Rescued', 'Fire_Alarm_System_Impact_on_Evacuation',
                            'Smoke_Alarm_at_Fire_Origin_Alarm_Type',
                            'Ext_agent_app_or_defer_time', 'TFS_Alarm_Time', 'TFS_Arrival_Time',
                            'Last_TFS_Unit_Clear_Time'], axis=1)

        # Declare the features and the target.
        self.X = df2.loc[:, df2.columns != 'Estimated_Dollar_Loss']
        self.X.drop("Unnamed: 0", axis=1, inplace=True)
        self.y = df2['Estimated_Dollar_Loss']

        self.scaler = StandardScaler()
        # Fit the independent variables (calculate the mean and standard deviation feature-wise)
        self.scaler.fit(self.X)
        # Scale the features and store them in a new variable
        self.X = self.scaler.transform(self.X)
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, test_size=0.3,
                                                                                random_state=42)

        # Create a KFold object with 5 splits
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        # Create a Gradient Boosting Regressor model with the best parameteres after grid search
        best_parameters = {'learning_rate': 0.1, 'max_depth': 3, 'n_estimators': 200}
        gbr = GradientBoostingRegressor(random_state=42,
                                        learning_rate=best_parameters['learning_rate'],
                                        max_depth=best_parameters['max_depth'],
                                        n_estimators=best_parameters['n_estimators'])
        self.gbr = gbr
        # Perform cross-validation
        cv_results = cross_val_score(self.gbr, self.X, self.y, cv=kf, scoring='neg_mean_squared_error')
        # Fit the model on the whole dataset
        self.gbr.fit(self.X_train, self.y_train)

        # Save the trained model to a file
        with open("./supervised_learning/gbr_model.pkl", "wb") as f:
            pickle.dump(self.gbr, f)
        # Save the encoders to files
        with open("./supervised_learning/ordinal_encoder.pkl", "wb") as f:
            pickle.dump(self.ordinal_encoder, f)
        # Save the scaler to files
        with open("./supervised_learning/scaler.pkl", "wb") as f:
            pickle.dump(self.scaler, f)
        # Save the DataFrame to a pickle file
        df2.to_pickle("./supervised_learning/fire_knowledge_processed.pkl")

    def load_model(self):
        # Load the trained model from the file
        with open("./supervised_learning/gbr_model.pkl", "rb") as f:
            self.gbr = pickle.load(f)

        # Load the encoders from files
        with open("./supervised_learning/ordinal_encoder.pkl", "rb") as f:
            self.ordinal_encoder = pickle.load(f)

        with open("./supervised_learning/scaler.pkl", "rb") as f:
            self.scaler = pickle.load(f)

        # Load the DataFrame from the pickle file
        self.df = pd.read_pickle("./supervised_learning/fire_knowledge_processed.pkl")

    def test_model(self):
        # use the trained model to make predictions on the test set
        y_pred_test = self.gbr.predict(self.X_test)
        # print("Y_PRED_TEST: ", y_pred_test)
        # check these predictions using the actual Estimated Dollar Loss
        df2 = pd.DataFrame(y_pred_test, columns=['Prediction'])
        df2['Prediction'] = np.exp(y_pred_test)
        # To get a proper result of the y_test column, we must reset the index and drop the old indexing
        y_test = self.y_test.reset_index(drop=True)
        # Let's overwrite the 'Target' column with the appropriate values
        # Again, we need the exponential of the test log Dollar Loss
        df2['Actual'] = np.exp(y_test)
        print(df2)

        # compute the RMSE on the test set
        rmse_test = mean_squared_error(self.y_test, y_pred_test, squared=False)
        mae = mean_absolute_error(self.y_test, y_pred_test)
        msle = mean_squared_log_error(np.exp(self.y_test), np.exp(y_pred_test))

        r2_score = sklearn.metrics.r2_score(self.y_test, y_pred_test)
        print("The R-Squared {.2f}%".format(r2_score))
        print("RMSE: {:.2f}".format(rmse_test))
        print('MAE:', mae)
        print('Mean Squared Log Error (MSLE):', msle)

    def predict_value(self, x_predict):
        # Applica la trasformazione con lo scaler
        x_scaled = self.scaler.transform(x_predict)
        # print("Stimando il valore di perdita economica: ")
        # Eseguire la previsione sul nuovo campione
        y_pred_new = self.gbr.predict(x_scaled)
        # print("Previsione per il nuovo campione LOG:", y_pred_new)
        # print("Previsione per il nuovo campione:", np.exp(y_pred_new))
        return np.exp(y_pred_new)


if __name__ == '__main__':
    estimator = Estimator()
    estimator.test_model()
    df_copy = estimator.df.drop(columns=['Estimated_Dollar_Loss'])
    first_row = estimator.X_test[0].reshape(1, -1)
    print(first_row)
    print("Y_TEST_0: ", estimator.X_test[0])
    estimator.predict_value(first_row)
