import sys
import pandas as pd
import numpy as np
import re
from operator import itemgetter
from statistics import mean
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, ENGLISH_STOP_WORDS
from sklearn.naive_bayes import MultinomialNB, GaussianNB
from sklearn.preprocessing import LabelEncoder, normalize
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.base import TransformerMixin
from sklearn.svm import LinearSVC, SVC
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.neural_network import MLPClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.linear_model import SGDClassifier

class StanceClassification:
    def __init__(self):

        self.train_x = None
        self.train_y = None

    def read_data(self, data_file1, data_file2):

        df1 = pd.read_csv(data_file1, encoding = "ISO-8859-1")
        df2 = pd.read_csv(data_file2, encoding = "ISO-8859-1")
        selected_df1 = df1[['body','isHK']]
        # print(selected_df1)
        all_data = pd.DataFrame(columns=['body','isHK'])
        all_data['body'] = df2['title'].map(str) + df2['text'].map(str)
        all_data['isHK'] = df2['isHK']
        all_data = all_data.append(selected_df1, ignore_index=True)

        self.train_x = np.asarray(all_data['body'])
        print("Number of samples: %d" % len(self.train_x))

        self.train_y = all_data['isHK']
        # self.train_y = LabelEncoder().fit_transform(self.train_y)
        # print(all_data)
        # all_data.to_csv("output.csv")

        return all_data

    # Start: Only useful when apply the linear classifier to the model
    # def print_top20(self, vectorizer, clf):
    #     # Prints features with the highest coefficient values, per class
    #     feature_names = vectorizer.get_feature_names()
    #
    #     top20_index = np.argsort(clf.coef_[0])[-20:]
    #     print("Top 20 features : %s" % (", ".join(feature_names[i] for i in top20_index)))
    # End

    def crossValidation(self, model_tag):
        scores = []
        f1_scores = []
        skf = StratifiedKFold(n_splits=5, shuffle=True)
        additional_stop_words = ['https','http','amp','com','reddit','www']
        for train_index, test_index in skf.split(self.train_x, self.train_y):
            if model_tag == 0:
                model = Pipeline([("ngram", CountVectorizer(stop_words=ENGLISH_STOP_WORDS.union(additional_stop_words), ngram_range=(1, 3), min_df=2, max_features=1000)),
                				  ("tfidf", TfidfTransformer()),
                                  ("clf", MultinomialNB())])
            elif model_tag == 1:
                model = Pipeline([("ngram", CountVectorizer(stop_words=ENGLISH_STOP_WORDS.union(additional_stop_words), ngram_range=(1, 3), min_df=2, max_features=1000)),
                				  ("tfidf", TfidfTransformer()),
                                  ("clf", SVC(C=1.0, gamma='scale', kernel='linear'))])
            elif model_tag == 2:
                model = Pipeline([("ngram", CountVectorizer(stop_words=ENGLISH_STOP_WORDS.union(additional_stop_words), ngram_range=(1, 3), min_df=2, max_features=1000)),
                				  ("tfidf", TfidfTransformer()),
                                  ("clf", AdaBoostClassifier())])
            elif model_tag == 3:
                model = Pipeline([("ngram", CountVectorizer(stop_words=ENGLISH_STOP_WORDS.union(additional_stop_words), ngram_range=(1, 3), min_df=2, max_features=1000)),
                				  ("tfidf", TfidfTransformer()),
                                  ("clf", SGDClassifier(loss='hinge', penalty='l1',
									alpha=1e-3,
									max_iter=1000, tol=1e-3))])
            # SVC(C=1.0, kernel='linear', gamma='auto')
            # LinearSVC(penalty='l1', dual= False, max_iter=1000)
            # SVC(C=1.0, kernel='sigmoid', gamma='scale')
            model.fit(self.train_x[train_index], self.train_y[train_index])
            predicted = model.predict(self.train_x[test_index])
            scores.append(accuracy_score(predicted, self.train_y[test_index]))
            f1_scores.append(f1_score(self.train_y[test_index], predicted))

            # Start: This part is used for error analysis
            # count = 0
            # error_text = []
            # for k in range(len(predicted)):
            #     if predicted[k] != self.train_y[test_index][k]:
            #         count += 1
            #         error_text.append((k, self.train_x[test_index][k]))
            #     if count == 10:
            #         break
            #
            # for error in error_text:
            #     print(error)
            # End

            # Start: This part is used for top 20 feature output
                #self.print_top20(model.named_steps['ngram'],model.named_steps['clf'])
            features_matrix = model.named_steps['ngram'].fit_transform(self.train_x[train_index], self.train_y[train_index])
            top20_best = SelectKBest(chi2, k=20)
            top20_best.fit_transform(features_matrix, self.train_y[train_index])
            feature_names = model.named_steps['ngram'].get_feature_names()

            top20_index = [i for i, x in enumerate(top20_best.get_support()) if x]
            print("Top 20 features : %s" % (", ".join(feature_names[i] for i in top20_index)))
            # End

        print("\nF1-measure: ", mean(f1_scores))
        return (scores)

def main():
    data_file1 = "comment_activity_with_tags.csv"
    data_file2 = "post_activity_with_tags.csv"
    # scores = []

    nlp_model = StanceClassification()
    
    nlp_model.read_data(data_file1, data_file2)
    # print("----Use N-gram Model----")

    # scores1 = nlp_model.crossValidation(0)
    # print("Naive Bayes Accuracy: %.16f \n" % mean(scores1))
    scores2 = nlp_model.crossValidation(1)
    print("SVM Accuracy: ", mean(scores2))
    # scores3 = nlp_model.crossValidation(2)
    # print("Ada Boost Accuracy: ", mean(scores3))
    scores4 = nlp_model.crossValidation(3)
    print("SGD Accuracy: ", mean(scores4))

    # Start: This part is used for feature selection
    # for i in range(5, 14):
    #     for j in range(i + 1, 14):
    #         scores3= nlp_model.crossValidation(topic_data, 3, i, j)
    #         scores.append((mean(scores3),i,j))
    #         print("Naive Bayes Accuracy: ", mean(scores3))
    #         print("i:", i)
    #         print("j:", j)
    # res = max(scores, key=itemgetter(0))
    # print("Best Naive Bayes Accuracy: ", res)
    # End



if __name__ == '__main__':
    main()