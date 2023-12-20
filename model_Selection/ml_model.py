from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pandas as pd

def preprocess_data_classification(df):
    target_column = df.columns[-1]
    feature_columns = df.columns[:-1]

    categorical_columns = df.select_dtypes(include=['object']).columns
    numeric_columns = df.select_dtypes(include=['number']).columns

    if categorical_columns.any():
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numeric_columns),
                ('cat', OneHotEncoder(drop='first'), categorical_columns)
            ], remainder='passthrough')

        classifier = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', LogisticRegression())
        ])

        X = df[feature_columns]
        y = df[target_column]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        classifier.fit(X_train, y_train)

        y_pred = classifier.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        classification_report_str = classification_report(y_test, y_pred)

        return df, target_column, feature_columns, accuracy, classification_report_str

    else:
        return df, target_column, feature_columns, None, None

def random_forest_classification(df):
    df, target_column, feature_columns, _, _ = preprocess_data_classification(df)

    if df is None:
        return None, None

    X = df[feature_columns]
    y = df[target_column]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    classifier = RandomForestClassifier()
    classifier.fit(X_train, y_train)

    y_pred = classifier.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    classification_report_str = classification_report(y_test, y_pred)

    return accuracy, classification_report_str

