import numpy as np
import cv2


class Interfaces:
    def __init__(self):
        pass

    def getFrame(self, cap):
        ret, frame = cap.read()
        if frame != None:
            # Convert the V channel of the HSV image into 8-bit unsigned,
            # so that it can be used with the thresholding routine.
            #frame2 = np.asarray([], dtype = "uint8")
            frame2 = np.copy(frame)
            for i in range(0, len(frame2)):
                frame2[i] = cv2.threshold(frame2[i].astype("uint8"),
                                         25, 255, cv2.THRESH_OTSU)[1]
            return [[frame, "frame1"], [frame2, "frame2"]]
        return [[None, "File end Reached"]]

    def runMainMenu(self):
        print "Please enter the file or file and folder of the .mp4 format footage for review or enter to use test footage:"
        footage = self.GetFileName()
        print "Menu"
        print "1. Normal Running Mode"
        print "2. Developer Mode"
        print "3. Exit"
        return self.GetMainMenuOption(), footage

    def GetFileName(self):
        while True:
            inp = raw_input()
            if len(inp) > 5 and inp[-4:-1] == ".mp4":
                try:
                    cap = cv2.VideoCapture(inp)
                    return cap
                except:
                    print "The file selected was not able to be opened"
            elif len(inp) == 0:
                try:
                    cap = cv2.VideoCapture("images/MVI_0360.mp4")
                    return cap
                except:
                    print "Expected Test Footage could not be found"

    def GetMainMenuOption(self):
        while True:
            i = str(raw_input("Please select from the displayed options:"))
            if i in ['N', 'NR', "n", 'nr', 'NRM', 'nrm', '1', '0']:
                print "Entering Normal Running Mode"
                return 1
            if i in ['d', 'D', 'dm', 'DM', '2']:
                print "Entering Developer Mode"
                return 2
            if i in ['e', 'E', "3", 'q']:
                print "Ending Program"
                print "Thanks for using this System for Counting Cars"
                return 3
            else:
                print "Please enter a valid menu option from above:"

    def DisplayImages(self, images):
            for i in images:
                cv2.imshow(i[1], i[0])

    def printcorrelation(self, correlation):
        string = ""
        count = 0
        for i in correlation:
            for ele in i:
                if len(ele) > 0 and len(ele[0]) >0:
                    string += "\nItem " + str(count) + ": " + str(ele[0][0]) + ", " + str(ele[0][1])
                count +=1
        return string


