import numpy as np
import matplotlib.pyplot as plt
import h5py
from sklearn import metrics
import seaborn as sn

#Activation Function
def sigmoid(x):
    y = 1 / (1 + np.exp(-x))
    return y

def sigmoid_derivative(x):
    y = sigmoid(x) * (1 - sigmoid(x))
    return y

def relu(x):
    return np.maximum(0, x)

def relu_derivative(x):
    x[x <= 0] = 0
    x[x > 0] = 1
    return x

def cost(m, y, output):
    return (-1) * (1/m) * (np.sum((y * np.log(output)) + ((1 - y) * (np.log(1 - output)))))

def cost_derivative(m, y1, y2):
    return (-1/m) * ((y1/y2) + (y1-1) * (1/(1-y2)))

def flatten(x):
    return x.reshape(x.shape[0], -1).T

class NeuralNetwork:
    def __init__(self, X_train, y_train, X_test, y_test, learning_rate, epochs):
        self.input = X_train
        self.y = y_train
        self.input_test = X_test
        self.test_label = y_test
        self.m = X_train.shape[1]
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.Loss_list = []
        self.epochs_list = []
        self.activation_value = []

    def weight_init(self):
        self.w = np.random.randn(self.input.shape[0], 1) * np.sqrt(2.0 / self.input.shape[1])

        return self.w

    def bias_init(self):
        self.b = 0.1
        self.bw = np.zeros((1, 1))
        return self.bw

    def feedforward(self, i):

        if i == 0:
            self.w = self.weight_init()
            self.b = self.bias_init()

        self.z = np.dot(self.w.T, self.input) + self.b * self.bw

        self.output = sigmoid(self.z)

        self.cost = (-1) * (1/self.m) * (np.sum((self.y * np.log(self.output)) + ((1 - self.y) * (np.log(1 - self.output)))))
        return self.output, self.cost

    def backpropogation(self):
        dw = np.dot((cost_derivative(self.m, self.y, self.output) * sigmoid_derivative(self.z)), self.input.T).T
        db = np.sum(cost_derivative(self.m, self.y, self.output) * sigmoid_derivative(self.z))

        self.w = self.w - self.learning_rate * dw
        self.bw = self.bw - self.learning_rate * db
        return self.w,  self.bw

    def propogation(self, i):
        self.a, self.cost = self.feedforward(i)
        self.w, self.bw = self.backpropogation()
        return self.a, self.cost, self.w, self.bw

    def fit(self):

        for i in range(self.epochs):

            self.a, self.cost, self.w, self.b = self.propogation(i)

            print('epochs:' + str(i) + " "
                  "| Loss:" + str(self.cost) + " "
                  "| Accuracy: {} %".format(100 - np.mean(np.abs(self.a - self.y)) * 100))

            if i % 100 == 0:

                self.activation_value.append(self.a.mean())
                self.Loss_list.append(self.cost)
                self.epochs_list.append(i)

        #Plotting Loss
        Loss_array = np.array(self.Loss_list)
        y_loss = Loss_array.reshape(-1, 1)
        x_epochs = np.array(self.epochs_list).reshape(-1, 1)

        plt.plot(x_epochs, y_loss)
        plt.xlabel('epochs')
        plt.ylabel('Loss')

        fig1 = plt.gcf()
        plt.show()
        fig1.savefig('epochs_vs_Loss.png')

        # Plotting activation
        activation_value = np.array(self.activation_value)
        activation_value = activation_value.reshape(-1, 1)
        x_epochs = np.array(self.epochs_list).reshape(-1, 1)

        plt.plot(x_epochs, activation_value)
        plt.xlabel('x_epochs')
        plt.ylabel('activation_value')

        fig2 = plt.gcf()
        plt.show()
        fig2.savefig('epochs_vs_activation_value.png')

        print("Training accuracy: {} %".format(100 - np.mean(np.abs(self.a - self.y)) * 100))

        return self.w, self.b

    def predict(self, x, threshold):

        probablity = sigmoid(np.dot(self.w.T, x) + self.b * self.bw)

        probablity[probablity <= threshold] = 0
        probablity[probablity > threshold] = 1

        y_predicted = probablity.astype(int)

        return y_predicted

    def confusion_matrix(self, y_test, y_predicted):

        y_predicted = np.squeeze(y_predicted)
        y_test = np.squeeze(y_test)
        cm = metrics.confusion_matrix(y_test, y_predicted)

        plt.figure(figsize=(10, 7))
        sn.heatmap(cm, annot=True, fmt='d')
        plt.xlabel("Predicted")
        plt.ylabel("Truth")
        plt.show()

    def evaluate(self, y_test, y_predicted):

        y_predicted = np.squeeze(y_predicted)
        y_test = np.squeeze(y_test)
        cm = metrics.confusion_matrix(y_test, y_predicted)

        TP = cm[0, 0]
        FP = cm[0, 1]
        FN = cm[1, 0]
        TN = cm[1, 1]

        accuracy = (TP + TN) / float(TP + TN + FP + FN)
        print('Testing accuracy: {} %'.format(accuracy*100))

        precision = TP / (TP + FP)
        print('Precision: {} %'.format(precision*100))

        recall = TP / (TP + FN)
        print('Recall: {} %'.format(recall*100))

        f1_score = 2 * ((precision * recall)/(precision + recall))
        print('F1_score: {} %'.format(f1_score * 100))

def load_dataset():
    train_dataset = h5py.File('datasets/train_catvnoncat.h5', "r")
    train_set_x_orig = np.array(train_dataset["train_set_x"][:])  # your train set features
    train_set_y_orig = np.array(train_dataset["train_set_y"][:])  # your train set labels

    test_dataset = h5py.File('datasets/test_catvnoncat.h5', "r")
    test_set_x_orig = np.array(test_dataset["test_set_x"][:])  # your test set features
    test_set_y_orig = np.array(test_dataset["test_set_y"][:])  # your test set labels

    classes = np.array(test_dataset["list_classes"][:])  # the list of classes

    train_set_y_orig = train_set_y_orig.reshape((1, train_set_y_orig.shape[0]))
    test_set_y_orig = test_set_y_orig.reshape((1, test_set_y_orig.shape[0]))

    return train_set_x_orig, train_set_y_orig, test_set_x_orig, test_set_y_orig, classes

if __name__ == '__main__':

    X_train, y_train, X_test, y_test, classes = load_dataset()

    X_train_flatten = flatten(X_train)
    X_test_flatten = flatten(X_test)

    X_train = X_train_flatten / 255
    X_test = X_test_flatten / 255

    model = NeuralNetwork(X_train, y_train, X_test, y_test, epochs=5000, learning_rate=0.01)
    model.fit()

    y_predicted = model.predict(X_test, threshold=0.3)
    #print('y_predicted: ' + str(y_predicted))
    #print('y_test_label: ' + str(y_test))
    #print('y_test: ' + str(classes[np.squeeze(y_test[:, 49])].decode('utf-8')))

    model.confusion_matrix(y_test, y_predicted)

    model.evaluate(y_test, y_predicted)