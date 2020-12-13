from datetime import date
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, recall_score, plot_roc_curve
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
# Django
from django.core.management.base import BaseCommand
from django_pandas.io import read_frame
from django.db.models import Q

from apps.training.models import Person, MedicalTest, EMRProperty


class Command(BaseCommand):
    help = 'Heart disease risk prediction'

    def handle(self, *args, **options):
        np.random.seed(1)

        self.stdout.write(self.style.SUCCESS('Process started'))

        persons = Person.objects.filter(
            Q(id__in=MedicalTest.objects.values_list('person_id').distinct('person_id')) & Q(
              id__in=EMRProperty.objects.values_list('person_id').distinct('person_id'))).distinct('id').order_by('id')

        last_medical_tests = MedicalTest.objects.filter(person_id__in=persons).order_by(
            'person_id', 'property_id', '-end_date').distinct('person_id', 'property_id')

        last_emr_properties = EMRProperty.objects.filter(person_id__in=persons).order_by(
            'person_id', 'property_id', '-end_date').distinct('person_id', 'property_id')

        df0 = read_frame(persons.filter(
            id__in=last_medical_tests.values_list('person_id')).order_by('id'))[['id', 'birthdate', 'sex', 'heart_disease_risk']].set_index('id')
        df0.sort_values('id', ascending=True, inplace=True)

        today = date.today()
        df0['birthdate'] = pd.to_datetime(df0['birthdate'], format='%Y-%m-%d')
        df0['age'] = df0.apply(
            lambda x: today.year - x['birthdate'].year - ((today.month, today.day) < (x['birthdate'].month, x['birthdate'].day)), axis=1)
        df0['gender'] = df0.apply(lambda x: 1 if x['sex'] == 'М' else 0,  axis=1)

        tmp_df1 = read_frame(last_medical_tests)[['person', 'property_name', 'property_value']]
        tmp_df1['person'] = pd.to_numeric(tmp_df1['person'], errors='coerce')
        tmp_df1.sort_values('person', ascending=True, inplace=True)
        piv1 = pd.pivot_table(tmp_df1, values='property_value', index=['person'], columns=['property_name'], aggfunc=np.sum, fill_value=0)
        df1 = pd.DataFrame(piv1.to_records())

        tmp_df2 = read_frame(last_emr_properties)[['person', 'property_name', 'property_value']]
        tmp_df2['person'] = pd.to_numeric(tmp_df2['person'], errors='coerce')
        tmp_df2.sort_values('person', ascending=True, inplace=True)
        piv2 = pd.pivot_table(tmp_df2, values='property_value', index=['person'], columns=['property_name'], aggfunc=np.sum, fill_value=0)
        df2 = pd.DataFrame(piv2.to_records())

        # Init total dataframe
        df = pd.concat([df1, df2], axis=1)
        df['id'] = df0.index
        df = df.reset_index().set_index('id')
        df['heart_disease_risk'] = df0['heart_disease_risk']
        df['age'] = df0['age']
        df['gender'] = df0['gender']
        # print(df['nan'].value_counts())
        # print(df.dtypes)
        # print(df.describe())

        # Split into training data and test data
        target = df['heart_disease_risk']
        df = df[['холестерин', 'рост', 'масса тела', 'индекс массы тела', 'SYS на левой руке', 'DIA на левой руке',
                 'SYS на правой руке', 'DIA на правой руке',  'age', 'gender', 'плотность (удельный вес)', 'СОЭ',
                 'общий билирубин', 'NEUT (сегментоядерные нейтрофилы)', 'HGB (гемоглобин)', 'NEUT#', 'LYM (лимфоциты)',
                 'WBC (лейкоциты)', 'уровень АлАТ', 'уровень АсАТ', 'палочкоядерные нейтрофилы', 'MONO (моноциты)',
                 'EO (эозинофилы)', 'уробилин (количественно)', 'глюкоза (капиллярная кровь)', 'количество']]
        df = df.apply(pd.to_numeric, errors='coerce')
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(0)
        X = df
        y = target
        print(df)
        # print(df.columns.tolist())

        # # Create training and testing vars, It’s usually around 80/20 or 70/30.
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.8, random_state=1437)

        # # Now we’ll fit the model on the training data
        model = RandomForestClassifier()
        model.fit(X_train, y_train)

        # # Make predictions on validation dataset
        # # predictions = model.predict(X_test)

        # # Pickle model
        pd.to_pickle(model, r'new_model.pickle')

        # # Unpickle model
        model = pd.read_pickle(r'new_model.pickle')
                
        # # Take input from user
        # cholesterol = float(input('Enter cholesterol (mMol/L): '))
        # height = float(input('Enter height (cm): '))
        # body_mass = float(input('Enter body mass (kg): '))
        # body_mass_index = float(input('Enter body mass index (number): '))
        # SYS_on_left_hand = float(input('Enter SYS on the left hand (number): '))
        # DIA_on_left_hand = float(input('Enter DIA on the left hand (number): '))
        # SYS_on_right_hand = float(input('Enter SYS on the right hand (number): '))
        # DIA_on_right_hand = float(input('Enter DIA on the right hand (number): '))
        # age = float(input('Enter age (years): '))
        # gender = float(input('Enter gender (0 or 1): '))
        # density_specific_gravity = float(input('Enter density (specific gravity) (g/l): '))
        # ESR = float(input('Enter ESR (СОЭ) (mm/h): '))
        # total_bilirubin = float(input('Enter total bilirubin (μMol/L): '))
        # NEUT_segmented_neutrophils = int(input('Enter NEUT (segmented neutrophils) (%): '))
        # hemoglobin = float(input('Enter hemoglobin (g/l): '))
        # NEUT = float(input('Enter NEUT (*10^9/l): '))
        # lymphocytes = float(input('Enter lymphocytes (%): '))
        # leukocytes = float(input('Enter leukocytes (*10^9/l): '))
        # AlAT_level = float(input('Enter AlAT level (U/L): '))
        # AsAT_level = float(input('Enter AsAT level (U/L): '))
        # sticknuclear_neutrophils = float(input('Enter sticknuclear neutrophils (%): '))
        # monocytes = float(input('Enter monocytes (%): '))
        # eosinophils = float(input('Enter eosinophils (%): '))
        # urobilin_quantitative = float(input('Enter urobilin (quantitative) (mMol/L): '))
        # glucose_capillary_blood = float(input('Enter glucose (capillary blood) (mMol/L): '))
        # amount_of_urine = float(input('Enter amount of urine (ml): '))

        # # # input must be 2D array
        # result = model.predict(
        #     [[cholesterol, height, body_mass, body_mass_index, SYS_on_left_hand, DIA_on_left_hand,
        #       SYS_on_right_hand, DIA_on_right_hand, age, gender, density_specific_gravity, ESR, total_bilirubin,
        #       NEUT_segmented_neutrophils, hemoglobin, NEUT, lymphocytes, leukocytes, AlAT_level, AsAT_level,
        #       sticknuclear_neutrophils, monocytes, eosinophils, urobilin_quantitative, glucose_capillary_blood,
        #       amount_of_urine]])
        # print('------------')
        # print('Result:')
        # print('------------')
        # print(result)
        print('------------')
        print('Train score:')
        print('------------')
        print(model.score(X_train, y_train))
        print('------------')
        print('Test score:')
        print('------------')
        print(model.score(X_test, y_test))
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
        sns.set(font_scale = 10)
        sns.set(style="whitegrid", color_codes=True, font_scale = 4.7)
        fig, ax = plt.subplots()
        fig.set_size_inches(90,45)
        sns.barplot(x=importances['Gini-Importance'], y=importances['Features'], data=importances, color='skyblue')
        plt.xlabel('Importance', fontsize=65, weight = 'bold')
        plt.ylabel('Features', fontsize=65, weight = 'bold')
        plt.title('Feature Importance', fontsize=65, weight = 'bold')
        print(importances)
        plt.savefig('importances.png')

        # pca_test = PCA(n_components=11)
        # pca_test.fit(X_train)
        # sns.set(style='whitegrid')
        # plt.plot(np.cumsum(pca_test.explained_variance_ratio_))
        # plt.xlabel('number of components')
        # plt.ylabel('cumulative explained variance')
        # plt.axvline(linewidth=4, color='r', linestyle = '--', x=0.2, ymin=0, ymax=11)
        # plt.savefig('PCA.png')
        # evr = pca_test.explained_variance_ratio_
        # cvr = np.cumsum(pca_test.explained_variance_ratio_)
        # pca_df = pd.DataFrame()
        # pca_df['Cumulative Variance Ratio'] = cvr
        # pca_df['Explained Variance Ratio'] = evr
        # print(pca_df.head(10))

        # ax = plt.gca()
        # rfc_disp = plot_roc_curve(model, X_test, y_test, ax=ax, alpha=0.8)
        # plt.savefig('ROC.png')

        # y_pred = model.predict(X_test)
        # # y_pred_gs = gs.best_estimator_.predict(X_test)

        # conf_matrix_baseline = pd.DataFrame(confusion_matrix(y_test, y_pred), index = ['actual 0', 'actual 1'], columns = ['predicted 0', 'predicted 1'])
        # # conf_matrix_tuned = pd.DataFrame(confusion_matrix(y_test, y_pred_gs), index = ['actual 0', 'actual 1'], columns = ['predicted 0', 'predicted 1'])
        # print(conf_matrix_baseline)
        # print('Baseline Random Forest recall score', recall_score(y_test, y_pred))
        # print(conf_matrix_tuned)
        # print('Hyperparameter Tuned Random Forest With PCA Reduced Dimensionality recall score', recall_score(y_test, y_pred_gs))