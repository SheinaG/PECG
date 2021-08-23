#include "stdio.h"
#include "stdlib.h"
#include "math.h"

double mykurtosis(double *data,int n) {
	
	int i;
	double mean,mean4,std,std4;

	mean=0;
	for (i=0;i<n;i++) {
		mean+=data[i];
	}
	mean/=n;
	std=0;
	mean4=0;
	for (i=0;i<n;i++) {
		std+=((data[i]-mean)*(data[i]-mean));
		mean4+=(pow((data[i]-mean),4));
	}
	std4=std*std;
	mean4*=n;
	return(mean4/std4);
}

int main(int argc,char *argv[]) {

	double x[5]={1.165, 0.6268, 0.0751, 0.3516, -0.6965};
	
	printf("Kurtosis of x[1.165, 0.6268, 0.0751, 0.3516, -0.6965] is %f\n",mykurtosis(x,5));

}
