from collections import Counter
import numpy as np
import tensorflow.examples.tutorials.mnist.input_data as input_data
mnist = input_data.read_data_sets("MNIST-data/", one_hot=True)


def read_file(filename):
    temp = np.load(filename)
    return temp["arr_0"]

def analysis_result(fileroad):
    print("================================================================")
    print(fileroad)
    print("----------------------------------------------------------------")
    end_pred = np.zeros((5, 10000))

    for t in (0,1,5,10,15,20,25,30,35,40):
        for i in range(1, 6):
            pred = read_file(
                "./C32_C64_F1024_F10/"+fileroad+"/pred"+str(t)+"_"+str(i)+".npz")
            pred = np.reshape(pred, [10000])
            acc = 0
            acc = np.mean(np.equal(pred, np.argmax(mnist.test.labels, 1)))
            print("net"+str(i)+" result:", acc)
            end_pred[i-1] = pred
        temp = np.zeros(10000)
        for j in range(10000):
            word_counts = Counter(end_pred[:, j])
            temp[j] = word_counts.most_common(1)[0][0]
        acc = np.mean(np.equal(temp, np.argmax(mnist.test.labels, 1)))
        print("microTraining times: %s \tbagging_result:{%.5f}" % (t, acc))

fileroad_scsf="Argu_Result_npz"
fileroad_dcdf="Argu_Result_npz_lastTwo"

analysis_result(fileroad_scsf)
analysis_result(fileroad_dcdf)