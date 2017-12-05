#include<opencv2/core/core.hpp>
#include<opencv2/highgui/highgui.hpp>
#include<opencv2/imgproc/imgproc.hpp>
#include<opencv2/opencv.hpp>
#include <stdio.h>
#include <math.h>
#include <string.h>
#include <iostream>
#include <fstream>
#include <sstream>
//#include <io.h>
//#include <atlbase.h>

using namespace std;
using namespace cv;

string imgpath = "E:\\大贝壳\\C++\\Lab\\Lab\\pic\\";
string savepath = "E:\\大贝壳\\C++\\Lab\\Lab\\Rect3(15)s\\";


Mat back, result;
int thresh = 50;
IplImage* img = NULL;
IplImage* img0 = NULL;
CvMemStorage* storage = NULL;

string imageName;

vector<string> getfiles(const string& dir, const string& extension, bool withpath){
	vector<string> filenames;
	string p;
	_tfinddata64_t file;
	intptr_t lf;
	if ((lf = _tfindfirst64(p.assign(dir).append("\\*.").append(extension).c_str(), &file)) == -1l)
		cout << "文件没有找到!\n";
	else
	{
		do
		{
			if (withpath){
				filenames.push_back(p.assign(dir).append("\\").append(file.name));

			}
			else{
				filenames.push_back(file.name);
			}
		} while (_tfindnext64(lf, &file) == 0);
	}
	_findclose(lf);

	sort(filenames.begin(), filenames.end());
	return filenames;
}





//angle函数用来返回（两个向量之间找到角度的余弦值）
double angle(CvPoint* pt1, CvPoint* pt2, CvPoint* pt0)
{
	double dx1 = pt1->x - pt0->x;
	double dy1 = pt1->y - pt0->y;
	double dx2 = pt2->x - pt0->x;
	double dy2 = pt2->y - pt0->y;
	return (dx1*dx2 + dy1*dy2) / sqrt((dx1*dx1 + dy1*dy1)*(dx2*dx2 + dy2*dy2) + 1e-10);
}

// 返回图像中找到的所有轮廓序列，并且序列存储在内存存储器中

CvSeq* findSquares4(IplImage* img, CvMemStorage* storage)
{
	CvSeq* contours;
	int i, c, l, N = 11;
	//矩形框的大小
	CvSize sz = cvSize(img->width & -2, img->height & -2);

	IplImage* timg = cvCloneImage(img);
	IplImage* gray = cvCreateImage(sz, 8, 1);
	IplImage* pyr = cvCreateImage(cvSize(sz.width / 2, sz.height / 2), 8, 3);
	IplImage* tgray;
	CvSeq* result;
	double s, t;

	// 创建一个空序列用于存储轮廓角点
	//CvSeq本身就是一个可增长的序列，不是固定的序列
	CvSeq* squares = cvCreateSeq(0, sizeof(CvSeq), sizeof(CvPoint), storage);


	//实例说明：cvSetImageROI(img1,cvRect(100,100,356,156))，
	//（100,100）	表示ROI区域的左上角坐标，356,156分别表示ROI区域的长宽。
	cvSetImageROI(timg, cvRect(0, 0, sz.width, sz.height));
	// 过滤噪音
	//图像金字塔，放大，缩小
	cvPyrDown(timg, pyr, 7);
	cvPyrUp(pyr, timg, 7);
	tgray = cvCreateImage(sz, 8, 1);

	// 红绿蓝3色分别尝试提取
	for (c = 0; c < 3; c++)
	{
		// 提取 the c-th color plane
		//cvSetImageCOI(IplImage* image, int coi):(A pointer to the image header,The channel of interest.)
		cvSetImageCOI(timg, c + 1);
		cvCopy(timg, tgray, 0);

		// 尝试各种阈值提取得到的（N=11）
		for (l = 0; l < N; l++)
		{
			// apply Canny. Take the upper threshold from slider
			// Canny helps to catch squares with gradient shading
			if (l == 0)
			{
				cvCanny(tgray, gray, 0, thresh, 5);
				//使用任意结构元素膨胀图像
				cvDilate(gray, gray, 0, 1);
			}
			else
			{
				// apply threshold if l!=0:
				cvThreshold(tgray, gray, (l + 1) * 255 / N, 255, CV_THRESH_BINARY);
			}

			// 找到所有轮廓并且存储在序列中
			cvFindContours(gray, storage, &contours, sizeof(CvContour),
				CV_RETR_LIST, CV_CHAIN_APPROX_SIMPLE, cvPoint(0, 0));

			// 遍历找到的每个轮廓contours
			while (contours)
			{
				//用指定精度逼近多边形曲线，
				//首先，轮廓的多边形逼近指的是：使用多边形来近似表示一个轮廓。
				//其次，多边形逼近的目的是为了减少轮廓的顶点数目。但多边形逼近的结果依然是一个轮廓，
				//只是这个轮廓相对要粗旷一些。
				/*	result = cvApproxPoly(contours, sizeof(CvContour), storage,
				CV_POLY_APPROX_DP, cvContourPerimeter(contours)*0.02, 0);*/




				result = cvApproxPoly(contours, sizeof(CvContour), storage,
					CV_POLY_APPROX_DP, cvContourPerimeter(contours)*0.04, 0);
				//cvContourPerimeter:轮廓 的周长



				//fabs：求绝对值
				/*		if (result->total == 4 &&
				fabs(cvContourArea(result, CV_WHOLE_SEQ)) > 500 &&
				fabs(cvContourArea(result, CV_WHOLE_SEQ)) < 100000 &&
				cvCheckContourConvexity(result))*/


				if (result->total == 4 &&
					fabs(cvContourArea(result, CV_WHOLE_SEQ)) > 500 &&
					fabs(cvContourArea(result, CV_WHOLE_SEQ)) < 150000 &&
					cvCheckContourConvexity(result))


					//该函数用于判断轮廓是否为凸(如果为凸返回值为 1，如果为凹返回0


				{
					s = 0;

					for (i = 0; i < 5; i++)
					{
						// find minimum angle between joint edges (maximum of cosine)
						if (i >= 2)
						{
							t = fabs(angle(
								(CvPoint*)cvGetSeqElem(result, i),
								(CvPoint*)cvGetSeqElem(result, i - 2),
								(CvPoint*)cvGetSeqElem(result, i - 1)));
							s = s > t ? s : t;
						}
					}

					// if 余弦值 足够小，可以认定角度为90度直角
					//cos0.1=83度，能较好的趋近直角
					if (s < 0.1)
					for (i = 0; i < 4; i++)
						cvSeqPush(squares,
						(CvPoint*)cvGetSeqElem(result, i));
				}

				// 继续查找下一个轮廓
				contours = contours->h_next;
			}
		}
	}
	cvReleaseImage(&gray);
	cvReleaseImage(&pyr);
	cvReleaseImage(&tgray);
	cvReleaseImage(&timg);

	return squares;
}

//drawSquares函数用来画出在图像中找到的所有正方形轮廓
Mat drawSquares(IplImage* img, CvSeq* squares)
{
	CvSeqReader reader;
	IplImage* cpy = cvCloneImage(img);
	int i;
	cvStartReadSeq(squares, &reader, 0);

	// read 4 sequence elements at a time (all vertices of a square)
	for (i = 0; i < squares->total; i += 4)
	{
		CvPoint pt[4], *rect = pt;
		int count = 4;

		// read 4 vertices
		CV_READ_SEQ_ELEM(pt[0], reader);
		CV_READ_SEQ_ELEM(pt[1], reader);
		CV_READ_SEQ_ELEM(pt[2], reader);
		CV_READ_SEQ_ELEM(pt[3], reader);

		// draw the square as a closed polyline
		cvPolyLine(cpy, &rect, &count, 1, 1, CV_RGB(0, 255, 0), 2, CV_AA, 0);
	}

	//cvShowImage(wndname, cpy);
	/*const char* filename = "111111111111111111111.jpg";
	const CvArr* image = cpy;
	int cvSaveImage("1111111111111111111111.jpg",image);*/
	//将Iplimage的cpy   图像向Mat 转换

	Mat back(cpy, true);






	//char* filename2 = "E:\\大贝壳\\C++\\opencvBlog\\Project1\\Project1\\pic\\Rect_img_233.jpg"; //图像名
	//cvSaveImage(filename2, cpy);//把图像写入文件



	//Mat mtx(cpy);

	cvReleaseImage(&cpy);



	return back;
}


//char* names[] = { "img_233.jpg", 0 };




int main(int argc, char** argv)
{
	int i, c;
	storage = cvCreateMemStorage(0);




	//for (i = 0; names[i] != 0; i++)
	//{
	//	img0 = cvLoadImage(names[i], 1);
	//	if (!img0)
	//	{
	//		cout << "不能载入" << names[i] << "继续下一张图片" << endl;
	//		continue;
	//	}





	vector<string> imageNames = getfiles(imgpath, "jpg", false);
	for (string imageName : imageNames) {
		cout << "processing image: " << imageName << endl;

		Mat srcImage = imread(imgpath + imageName);  //工程目录下应该有一张名为1.jpg的素材图

		//Mat srcImage 向 IplImage  img0转换


		IplImage imgTmp = srcImage;
		IplImage *img0 = cvCloneImage(&imgTmp);

		img = cvCloneImage(img0);
		//cvNamedWindow(wndname, 1);

		// find and draw the squares
		result = drawSquares(img, findSquares4(img, storage));


		imwrite(savepath + "_" + imageName, result);


		c = cvWaitKey(0);

		cvReleaseImage(&img);
		cvReleaseImage(&img0);

		cvClearMemStorage(storage);

		if ((char)c == 27)
			break;
	}


	return 0;
}

