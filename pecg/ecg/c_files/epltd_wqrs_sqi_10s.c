/*****************************************************************************
	07/07/06:
		Added the compare with WQRS to find noise segments using the Matt's
		algorithm. So the annot output is: time-detection time; anntyp-QRS for 
		beats, NOISE for kurtosis<5(non-ECG) or kurtosis>127(invalid data);
		subtyp- if <0 means kurtosis value and no WQRS annot, if >=0 means
		SQI of Matt's algorithm, 0-100 (matched/all detection beats for 10s), 
		if SQI>50, means Good Quality.
*******************************************************************************/

#include <wfdb/wfdb.h>
#include <wfdb/ecgcodes.h>
#include <wfdb/ecgmap.h>
#include "string.h"
#include "stdio.h"
#include "stdlib.h"
#include "math.h"


WFDB_Annotation annot,annot2;
FILE *fp;
char A, Aprime;		/* types of the current & next reference annotations */
char a, aprime;		/* types of the current & next test annotations */
int match_dt;		/* match window duration in samples */
long shut_down;		/* duration of test annotator's shutdown */
long start=0;		/* time of the beginning of the test period */
long end_time;		/* end of the test period (-1: end of reference annot
			   file; 0: end of either annot file) */
long huge_time = 0x7FFFFFFF;		/* largest possible time */
long T, Tprime;		/* times of the current & next reference annotations */
long t, tprime;		/* times of the current & next test annotations */

void myquit(char *tempfname2) 
{

    	wfdbquit();
		fscanf(fp,"%s",tempfname2);
}

void getref()	/* get next reference beat annotation */
{
    static long TT;	/* time of previous reference beat annotation */

    TT = T;
    T = Tprime;
    A = Aprime;


    while (getann(0, &annot) == 0) {
//		if (isqrs(annot.anntyp)) {	/* beat annotation */

	    		Tprime = annot.time;
			    Aprime = annot.anntyp;
	    		return;

//		}
    }
    /* When this statement is reached, there are no more annotations in the
       reference annotation file. */
    Tprime = huge_time;
    Aprime = '*';
}

void gettest()	/* get next test annotation of NOISE*/
{
    static long tt;	/* time of previous test beat annotation */

    tt = t;
    t = tprime;
    a = aprime;

    while (getann(1, &annot2) == 0) {
		if (isqrs(annot2.anntyp)) {
	    	tprime = annot2.time;
	    	aprime = annot2.anntyp;
	    	return;
		}
    }
    tprime = huge_time;
    aprime = '*';
}


char *ecglead[19]={"I","II","III","AVR","AVL","AVF","V","V1","V2","V3","V4","V5","V6","MCL1","MCL2","MCL3","MCL4","MCL5","MCL6"};


int main(int argc,char *argv[]) {
	char record[50], fname[50] ;
	long i;
	int j, ecg[20], delay, recNum ;
//	WFDB_Siginfo si[3] ;
	WFDB_Anninfo a[3] ;
	WFDB_Annotation annbuf[100];
	WFDB_Siginfo s[100];
	WFDB_Sample v[20];
	int annbufn;
	int leadi,leadj;

	char tempfname1[50],tempfname2[50],tempfname[100];
	int nsig,n;
	char *p;
	char tempname[10],tempname1[10],wqrsname[10],outname[10];
	int sp10s=10*125;
	double tempk;
	int iswqrs;
	int matchn,epltdn,wqrsn;
	int match_dt;
	long datalength;
	char tempsubtyp;

	// Set up path to database directory
	if (argc<2) {
		fprintf(stderr,"Usage: %s recordfile \n",argv[0]);
		exit(-1);
	}
	wfdbquiet();
	fp=fopen(argv[1],"r");
	if (fp==NULL) {
		fprintf(stderr,"Open recordfile - %s error!\n",argv[1]);
		exit(-1);
	}
	if ((p=index(argv[1],'.'))==NULL) {
		fprintf(stderr,"Recordfile - %s name style error!\n",argv[1]);
		exit(-1);
	}
	n=p-argv[1];
	for (i=0;i<n;i++)
		tempfname1[i]=argv[1][i];
	tempfname1[i++]='/';
	tempfname1[i]='\0';
	fscanf(fp,"%s",tempfname2);
	while (!feof(fp)) 
	{
		strcpy(tempfname,tempfname1);
		strcat(tempfname,tempfname2);
		strcat(tempfname,"/");
		strcat(tempfname,tempfname2);
		printf("\nProcessing %s ... \n",tempfname);

		strcpy(record,tempfname);

		nsig=isigopen(record,NULL,0);
		if(isigopen(record,s,nsig) < 1)	{
			printf("Couldn't open %s\n",record) ;
			return ;
		}
  		end_time=datalength=strtim("e");

		for (leadi=0;leadi<nsig;leadi++) 
		for (leadj=0;leadj<19;leadj++) 
			if (strcmp(s[leadi].desc,ecglead[leadj])==0) {


		strcpy(tempname1,"A");
		strcpy(tempname,"epltd");
		strcpy(wqrsname,"wqrs");
		strcpy(outname,"epsqi");
		
		tempname1[0]+=leadj;
		strcat(tempname,tempname1);
		strcat(wqrsname,tempname1);
		strcat(outname,tempname1);
		a[0].name = outname; a[0].stat = WFDB_WRITE;
		a[1].name = tempname; a[1].stat = WFDB_READ;
		a[2].name = wqrsname; a[2].stat = WFDB_READ;
		
				
		printf("\nECG: %s, leader: %s, annot file: %s\n",tempfname,ecglead[leadj],a[0].name);
		
		if(annopen(record, a, 3) < 0) {
			iswqrs=0;
			if(annopen(record, a, 2) < 0)
				return ;
		}
		else
			iswqrs=1;

		match_dt = (int)strtim(".15");
		start=10*125;

		T=t=0;
		Tprime=tprime=0;

		if (iswqrs==0) { // No WQRS annotation, just copy epltd to epsqi and set the subtyp is negative value.
			while (getann(0,&annot)==0) {
				if (annot.subtyp>=127) {
					annot.subtyp=-1;
					annot.anntyp=NOISE;
				}
				annot.subtyp = annot.subtyp>1?-annot.subtyp:-1;
				annot.num = leadj+1;

				putann(0,&annot);
			}
		}
		else { // Has WQRS annotation, compare epltd and wqrs within 10s
			do {
				getref();
			} while (T< start);

			do {
				gettest();
			} while (tprime < start);
			for (i=0;i<datalength;i+=sp10s) {
				matchn=epltdn=wqrsn=annbufn=0;
			    while ((end_time > 0L ) && (T < end_time  || t < end_time ) && (((T>=i) && (T<i+sp10s)) || ((t>=i) && (t<i+sp10s)))) {
					if (t < T) {	/* test annotation is earliest */
				    	if (T-t <= match_dt && (T-t < abs(T-tprime) || abs(Tprime-tprime) < abs(T-tprime))) {
							matchn++;
							annbuf[annbufn++]=annot;
							getref();
							gettest();
							epltdn++;
							wqrsn++;
				    	}
				    	else {
							gettest();
							wqrsn++;
		    			}
					}
					else {		/* reference annotation is earliest */
				    	if (t-T <= match_dt && (t-T < abs(t-Tprime) || abs(tprime-Tprime) < abs(t-Tprime))) {
							matchn++;
							annbuf[annbufn++]=annot;
							gettest();
							getref();
							epltdn++;
							wqrsn++;
				    	}
				    	else {
							annot.subtyp=-annot.subtyp; // No WQRS matched, set subtyp is negative.
							annbuf[annbufn++]=annot;
							getref();
							epltdn++;
	    				}
					}
				}
				if (annbufn>0) {
					if (wqrsn+epltdn-matchn>0) {
						tempsubtyp=(char)(1.0*matchn/(wqrsn+epltdn-matchn)*100);
//						if (tempsubtyp>100)
//							tempsubtyp=100;
					}
					else 
						tempsubtyp=0;
					for (j=0;j<annbufn;j++) {
						if (annbuf[j].anntyp==NOISE) {  // Kurtosis is bad, <5
							annot.subtyp=-abs(annot.subtyp);
						}
						if (abs(annbuf[j].subtyp)>=127) { // Kurtosis is bad, >127, invalid data
							annbuf[j].subtyp=-1;
							annbuf[j].anntyp=NOISE;
						}
						if (annbuf[j].subtyp>0) { // Non-NOISE and have WQRS matched, set SQI value
							annbuf[j].subtyp=tempsubtyp;
						}
						annbuf[j].num = leadj+1;
						putann(0,&annbuf[j]);
					}
				}
			}



		}
		}


		printf("Processing %s end \n",tempfname);
		myquit(tempfname2);


	}
}

