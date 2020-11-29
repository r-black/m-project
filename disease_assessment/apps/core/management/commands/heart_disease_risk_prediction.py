from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, recall_score
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np; np.random.seed(1)
# Django
from django.core.management.base import BaseCommand
from django_pandas.io import read_frame

from apps.api.models import Person, MedicalRecord


class Command(BaseCommand):
    help = 'Heart disease risk prediction'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Process started'))

        persons = Person.objects.filter(id__in=MedicalRecord.objects.values_list(
            'person_id').distinct()).order_by('id').values('id', 'age', 'gender', 'heart_disease_risk')
        medical_records = MedicalRecord.objects.order_by('person_id', '-row_number').distinct(
            'person_id').values('person_id', 'systolic_blood_pressure', 'diastolic_blood_pressure', 'heart_rate')

        # Init dataset
        df = pd.concat([read_frame(persons), read_frame(medical_records)], sort=False, axis=1)
        print(df)
        # print(df.describe())

        # Split into training data and test data
        X = df[['age', 'gender', 'systolic_blood_pressure', 'diastolic_blood_pressure', 'heart_rate']]
        y = df['heart_disease_risk']

        # Create training and testing vars, It’s usually around 80/20 or 70/30.
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.8, random_state=1, stratify=y)

        # Now we’ll fit the model on the training data
        model = RandomForestClassifier(
            bootstrap=True,
            class_weight=None,
            criterion='gini',
            max_depth=None,
            max_features='auto',
            max_leaf_nodes=None,
            min_impurity_decrease=0.0,
            min_impurity_split=None,
            min_samples_leaf=1,
            min_samples_split=2,
            min_weight_fraction_leaf=0.0,
            n_estimators=100,
            n_jobs=None,
            oob_score=False,
            random_state=1,
            verbose=0, 
            warm_start=False
        )
        model.fit(X_train, y_train)

        # Make predictions on validation dataset
        # predictions = model.predict(X_test)

        # Pickle model
        pd.to_pickle(model, r'new_model.pickle')

        # Unpickle model
        model = pd.read_pickle(r'new_model.pickle')

        # Take input from user
        age = int(input('Enter age: '))
        gender = int(input('Enter gender: '))
        systolic_blood_pressure = int(input('Enter systolic blood pressure: '))
        diastolic_blood_pressure = int(input('Enter diastolic blood pressure: '))
        heart_rate = int(input('Enter heart rate: '))

        # input must be 2D array
        result = model.predict(
            [[age, gender, systolic_blood_pressure, diastolic_blood_pressure, heart_rate]])
        print('------------')
        print('Result:')
        print('------------')
        print(result)
        print('------------')
        print('Train score:')
        print('------------')
        print(model.score(X_train, y_train))
        print('------------')
        print('Test score:')
        print('------------')
        print(model.score(X_test, y_test))
        print('------------')
        print('Predict proba:')
        print('------------')
        print(model.predict_proba(
            [[age, gender, systolic_blood_pressure, diastolic_blood_pressure, heart_rate]]))
        print('------------')
        print('Cross validation score:')
        print('------------')
        print(cross_val_score(model, X_train, y_train, cv=2))
        print('------------')

        y_pred = model.predict(X_test)
        result = confusion_matrix(y_test, y_pred)
        print("Confusion Matrix:")
        print(result)
        result1 = classification_report(y_test, y_pred)
        print("Classification Report:",)
        print (result1)
        result2 = accuracy_score(y_test,y_pred)
        print("Accuracy:",result2)

        feats = {}
        for feature, importance in zip(X.columns, model.feature_importances_):
            feats[feature] = importance
        importances = pd.DataFrame.from_dict(feats, orient='index').rename(columns={0: 'Gini-Importance'})
        importances = importances.sort_values(by='Gini-Importance', ascending=False)
        importances = importances.reset_index()
        importances = importances.rename(columns={'index': 'Features'})
        sns.set(font_scale = 5)
        sns.set(style="whitegrid", color_codes=True, font_scale = 1.7)
        fig, ax = plt.subplots()
        fig.set_size_inches(30,15)
        sns.barplot(x=importances['Gini-Importance'], y=importances['Features'], data=importances, color='skyblue')
        plt.xlabel('Importance', fontsize=25, weight = 'bold')
        plt.ylabel('Features', fontsize=25, weight = 'bold')
        plt.title('Feature Importance', fontsize=25, weight = 'bold')
        # display(plt.show())
        print(importances)
        plt.savefig('importances.png')

        pca_test = PCA(n_components=3)
        pca_test.fit(X_train)
        sns.set(style='whitegrid')
        plt.plot(np.cumsum(pca_test.explained_variance_ratio_))
        plt.xlabel('number of components')
        plt.ylabel('cumulative explained variance')
        plt.axvline(linewidth=4, color='r', linestyle = '--', x=1, ymin=0, ymax=1)
        plt.savefig('PCA.png')
        evr = pca_test.explained_variance_ratio_
        cvr = np.cumsum(pca_test.explained_variance_ratio_)
        pca_df = pd.DataFrame()
        pca_df['Cumulative Variance Ratio'] = cvr
        pca_df['Explained Variance Ratio'] = evr
        print(pca_df.head(10))

        y_pred = model.predict(X_test)
        # y_pred_gs = gs.best_estimator_.predict(X_test)

        conf_matrix_baseline = pd.DataFrame(confusion_matrix(y_test, y_pred), index = ['actual 0', 'actual 1'], columns = ['predicted 0', 'predicted 1'])
        # conf_matrix_tuned = pd.DataFrame(confusion_matrix(y_test, y_pred_gs), index = ['actual 0', 'actual 1'], columns = ['predicted 0', 'predicted 1'])
        print(conf_matrix_baseline)
        print('Baseline Random Forest recall score', recall_score(y_test, y_pred))
        # print(conf_matrix_tuned)
        # print('Hyperparameter Tuned Random Forest With PCA Reduced Dimensionality recall score', recall_score(y_test, y_pred_gs))