from datetime import date
from io import BytesIO
import model_card_toolkit as mctlib
from sklearn.datasets import make_moons
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import plot_roc_curve, plot_confusion_matrix

import base64
import matplotlib.pyplot as plt
import seaborn as sns
import uuid


NAME = 'Yevhen K.'
CONTACT = 'name@example.com'
CARD_NAME = 'RandomFores Classifier for MakeMoons Dataset'
CARD_OVERVIEW = 'Simple Card With RandomForest Classifier for Dummy Data'
REFERENCES = [
    'https://www.tensorflow.org/responsible_ai/model_card_toolkit/examples/Scikit_Learn_Model_Card_Toolkit_Demo',
    'https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html',
]
LIMITATIONS = 'Random forest classification of dummy dataset'
DESCRIPTION = 'Education with classification'
EXPORT_PATH = 'card.html'


# Utility function that will export a plot to a base-64 encoded string that the model card will accept.

def plot_to_str():
    img = BytesIO()
    plt.savefig(img, format='png')
    return base64.encodebytes(img.getvalue()).decode('utf-8')


def make_card(X_train, dataset_plot, analysis_plots):
    ##  Initialize toolkit and model card
    mct = mctlib.ModelCardToolkit()
    model_card = mct.scaffold_assets()

    model_card.model_details.name = CARD_NAME
    model_card.model_details.overview = (CARD_OVERVIEW)
    model_card.model_details.owners = [
        mctlib.Owner(name= NAME, contact=CONTACT)
    ]
    model_card.model_details.references = [
        mctlib.Reference(reference=reference) for reference in REFERENCES
    ]
    model_card.model_details.version.name = str(uuid.uuid4())
    model_card.model_details.version.date = str(date.today())

    model_card.considerations.limitations = [mctlib.Limitation(description=LIMITATIONS)]
    model_card.considerations.use_cases = [mctlib.UseCase(description=DESCRIPTION)]

    model_card.model_parameters.data.append(mctlib.Dataset())
    model_card.model_parameters.data[0].graphics.description = (
      f'{len(X_train)} rows with {len(X_train[0])} features')
    model_card.model_parameters.data[0].graphics.collection = [
        mctlib.Graphic(image=dataset_plot)
    ]
    
    model_card.quantitative_analysis.graphics.description = (analysis_plots["desc"])
    model_card.quantitative_analysis.graphics.collection = [
        mcvlib.Graphic(image=plot) for plot in analysis_plots["plots"]
    ]
    mct.update_model_card(model_card)
    return mct


def main():
    X, y = make_moons(n_samples=200, noise=0.3, random_state=0)
    X = StandardScaler().fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.4, random_state=42
    )
    clf = RandomForestClassifier(max_depth=5, 
        n_estimators=100, 
        criterion="gini",
        max_features=1, 
        random_state=1337)
    clf.fit(X_train, y_train)

    # Plot Dataset
    plt.title("Two moons", fontsize="small")
    plt.scatter(X[:, 0], X[:, 1], marker="o", c=y, s=25, edgecolor="k")
    dataset_plot = plot_to_str()

    # Plot a ROC curve
    plot_roc_curve(clf, X_test, y_test)
    roc_curve = plot_to_str()
    
    # Plot a confusion matrix
    plot_confusion_matrix(clf, X_test, y_test)
    confusion_matrix = plot_to_str()

    analysis_plots = {
        "desc": "ROC curve and confusion matrix",
        "plots": [roc_curve, confusion_matrix],
    }

    ### Create a model card
    mct = make_card(X_train, dataset_plot, analysis_plots)
    ### Generate model card
    # Return the model card document as an HTML page
    html = mct.export_format()
    with open(EXPORT_PATH, "wt") as f:
        f.write(html)
    
if __name__ == "__main__":
    main()
