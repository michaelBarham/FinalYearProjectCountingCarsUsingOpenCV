import numpy as np
import cv2

from Interfaces import Interfaces
from Correlation import Correlation


class DifferenceSystem:
    def __init__(self):
        self.interfaces = Interfaces()
        self.correlation = Correlation()

    def getDifference(self, frame, previousframe):
        frameDelta = cv2.absdiff(previousframe, frame)
        # frameDelta = cv2.cvtColor(frameDelta, cv2.COLOR_BGR2HSV)
        # frame = frame.astype ("uint8")
        # thresh = cv2.threshold(frame, 25, 255, cv2.THRESH_OTSU)[1]
        # cv2.THRESH_BINARY+
        # frameDelta = cv2.subtract(255,hsv)

        blur1 = cv2.GaussianBlur(frameDelta, (5, 5), 0)
        blur2 = cv2.GaussianBlur(frameDelta, (21, 21), 0)
        # ret,gray = cv2.adaptivethreshold(frameDelta.astype(np.int32),127,255,0)
        mask1 = cv2.inRange(frameDelta,
                            np.asarray([0, 0, 0], dtype="uint8"),
                            np.asarray([2, 2, 2], dtype="uint8"))
        mask2, contours, hierarchy = cv2.findContours(np.copy(mask1),
                                                      cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        # mask2 = np.copy(mask1)
        mask2 = cv2.GaussianBlur(mask2, (5, 5), 0)
        mask3 = np.copy(mask2)
        mask3 = cv2.erode(mask3, None, iterations=8)
        mask4 = np.copy(mask3)
        mask4 = cv2.dilate(mask4, None, iterations=2)
        blur3 = np.copy(mask4)
        blur3 = cv2.GaussianBlur(blur3, (21, 21), 0)

        # ret, thresh = cv2.threshold(yellow, 127, 255, 0)
        # print thresh.dtype

        # thresh = cv2.adaptiveThreshold(frameDelta.astype(np.uint8),255,1,1,11,2)

        # first frame to be original frame
        # last  frame to be used going forwards for getContour
        return [[frame, "frame"],
                [previousframe, "previousframe"],
                [frameDelta, "frameDelta"],
                [blur1, "blur1"],  # [blur2, "blur2"],
                [mask1, "mask1"], [mask2, "mask2"],
                # [mask3, "mask3"],
                [blur3, "blur3"],
                [mask4, "mask4"]]

    def getContours(self, frame):
        frame, contours, hierarchy = cv2.findContours(frame,
                                                      cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        areas = []
        for c in contours:
            areas.append(cv2.contourArea(c))

        max_index = np.argmax(areas)
        # contours.remove(max_index)
        contoursWithoutMax = []
        i = 0
        while i != max_index and i < len(areas):
            contoursWithoutMax.append(contours[i])
            i += 1
        contours = contoursWithoutMax
        return contours

        # contoursContentsImage = []
        # for c in contours:
        #    #cont = cv2.approxPolyDP(c, 3, False)
        #    #blur3 = cv2.drawContours(blur3, cont, -1, (0, 255, 0), thickness=10, lineType=8)
        #    contoursContentsImage.append(np.copy(frame)[x:y, w:h])
        #    frame2 = cv2.rectangle(frame2,(x,y),(x+w,y+h),(0,255,0),3)
        # think about thresholding with the threshold
        # value chosen using Otsu's algorithm

        # contoursContentsImage
        # np.clip(cap, 0, 255, out=previousframe)
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    def getContoursMovement(self, orgframe, pre2Cotrs, pre1Cotrs, curCotrs, loopCount):
        """
        calls inRange varient
        possible improves make preCon1 & 2 only hold x y h w values instead of other stuff
        """
        ls = []
        for currCon in curCotrs:
            x2, y2, w2, h2 = cv2.boundingRect(currCon)
            for preCon1 in pre1Cotrs:
                x1, y1, w1, h1 = cv2.boundingRect(preCon1)
                if self.inRangeOfPreContours([x1, y1, h1, w1], [x2, y2, h2, w2], 10, 5, 20, 20):
                    for preCon2 in pre2Cotrs:
                        x3, y3, w3, h3 = cv2.boundingRect(preCon2)
                        if self.inRangeOfPreContours([x3, y3, h3, w3], [x2, y2, h2, w2], 10, 5, 20, 20):  # 10, 10):
                            ls.append([x2 - x1, y2 - y1, h2, w2, currCon, preCon2])
                            if loopCount > 10:
                                orgframe = cv2.rectangle(orgframe, (x2, y2),
                                                         (x2 + w2, y2 + h2), (0, 255, 0), 4)
        return [[orgframe, "frame2"]], pre1Cotrs, ls

    def getMatches(self, ls, correlation, loopCount):
        count = 0
        countRepeatDetect = 0
        printstring = ""
        for li in correlation:
            if [] not in li:
                li.append([])
        listcount1 = 0
        listcount2 = 0
        while listcount1 < len(ls):
            while listcount2 < len(ls):
                if listcount1 != listcount2:
                    if self.inRangeOfPreContours(ls[listcount1], ls[listcount2], 4, 4, 10, 10):
                        correlation, printstring, count, countRepeatDetect = self.addNewOldCorrelate(ls[listcount1],
                                                                                                     correlation, count,
                                                                                                     countRepeatDetect,
                                                                                                     printstring,
                                                                                                     loopCount)
                listcount2 += 1
            listcount1 += 1
        li = 0

        while li < len(correlation):
            if len(correlation[li]) > 1 and correlation[li][0][0][0] == "new":
                correlation[li][-1].remove("new")
                print"removed"
            if len(correlation[li]) > 1:
                correlation[li] = correlation[li][1:]
            if len(correlation[li]) == 1:
                i = 0
                corUpdate = []
                while i < len(correlation):
                    if i != li:
                        corUpdate.append(correlation[i])
                    i += 1
                correlation = corUpdate
            li += 1
        return correlation, printstring, count, countRepeatDetect

    def addNewOldCorrelate(self, con1, correlation, count, countRepeatDetect, printstring, loopCount):
        carExist = False
        for li in correlation:
            if len(li[-1]) > 0 and li[-1][0][0] != "new":
                if self.inRangeOfPreContours(con1, li[len(li) - 1][0], 16, 4, 40, 40):
                    li = self.correlation.addElementContour(con1, li)
                    carExist = True
            elif len(li[-1]) > 0 and li[-1][0][0] == "new":
                if self.inRangeOfPreContours(con1, li[0][0], 16, 4, 40, 40):
                    li = self.correlation.addElementContour(con1, li)
                    carExist = True
            if carExist:
                printstring += " car "
                countRepeatDetect += 1
                break
        if carExist != True:
            # print "not pre car"
            correlation.append([[con1], [["new", "new", "new", "new"]]])
            printstring += "\nnew car found\n"
            if loopCount > 10:
                count += 1
            countRepeatDetect += 1
        # print "complete addNewOld"
        return correlation, printstring, count, countRepeatDetect

    def inRangeOfPreContours(self, con1, con2, Xrange, Yrange, hrange, wrange):
        return con1[0] in range(con2[0] - Xrange,
                                con2[0] + Xrange) and con1[1] in range(con2[1] - Yrange,
                                                                       con2[1] + Yrange) and con1[2] in range(
            con2[2] - hrange,
            con2[2] + hrange) and con1[3] in range(con2[3] - wrange,
                                                   con2[3] + wrange)

    def displayWithRect(self, img, conts):
        for i in conts:
            xlow = -1
            ylow = -1
            xmax = 0
            ymax = 0
            for li in i[-1]:
                if len(li) > 3:
                    print "entered if"
                    # find lowest x
                    if li[0] < xlow:
                        xlow = li[0]
                    elif xlow == -1:
                        xlow = li[0]
                    # find lowest y
                    if li[1] < ylow:
                        ylow = li[1]
                    elif ylow == -1:
                        ylow = li[1]
                    # find highest x
                    if (li[0] + li[2]) > xmax:
                        xmax = li[0] + li[2]
                    # find highest y
                    if (li[1] + li[3]) > ymax:
                        ymax = li[1] + li[3]
            if xlow != -1 and ylow != -1 and xmax != 0 and ymax != 0:
                print "successful display rect"
                img = cv2.rectangle(img, (xlow, ylow), (xmax, ymax), (255, 0, 0), 4)
        return img
