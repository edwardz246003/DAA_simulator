# -*- coding: utf-8 -*-
"""
Created on Fri Apr  6 22:55:42 2018

@author: Administrator
"""
from __future__ import unicode_literals
import time
import random
import math 
import numpy as np


def randNum2SolveTimeFunc(HR,randNum,difficulty):
	#print HR,' ',randNum,' ',difficulty
	p = 1.00/(difficulty*(2**40))
	#print p
	ST = -math.log(randNum)/p/HR
	#print 
	return ST

def getNextDiff_targetMean(iDSeri,iSTseri,iT,iN,height):
	sumTarget = 0.0
	nWeight = 0.0
	sum_time = 0.0
	for i in range(height-iN,height):  #range(height-iN+1,height)这个+1必须去掉，不然i只能取到iN-1个数字
		solvetime = iSTseri[i-1]
		if solvetime > 7*iT:
			 solvetime = 7*iT
		if solvetime < -6*iT:
			solvetime = -6*iT
		nWeight = nWeight + 1
		sum_time += solvetime * nWeight
		sumTarget = sumTarget + (2**(256-40))/iDSeri[i-1]
	if sum_time  < (iN*(iN+1)/2)* iT / 20 : 
		sum_time = (iN*(iN+1)/2)*iT / 20
	next_target = 2 * (sum_time/(iN*(iN+1)))* (sumTarget/iN)/iT
	next_Difficulty = (2**(256-40))/next_target
	if next_Difficulty  <  1:
		return 1
	return next_Difficulty
 
def getNextDiff_old(iDSeri,iSTseri,iT,iN,height):
	#iN必须>40
	bnAvg = 0.0
	nFirstBlockTime =0.0
	nLastBlockTime=0.0
	for i in range(height-iN,height-iN+30):  #range(height-iN+1,height)这个+1必须去掉，不然i只能取到iN-1个数字
         bnAvg =bnAvg+2**(256-40)/iDSeri[i]/30
	for i in range(height-iN,height-35):  #range(height-iN+1,height)这个+1必须去掉，不然i只能取到iN-1个数字
         nFirstBlockTime =nFirstBlockTime+iSTseri[i]
	for i in range(height-iN,height-5):  #range(height-iN+1,height)这个+1必须去掉，不然i只能取到iN-1个数字
         nLastBlockTime =nLastBlockTime+iSTseri[i]   
	nActualTimespan = nLastBlockTime - nFirstBlockTime
	nPowMaxAdjustUp=16;
	nPowMaxAdjustDown=32;
	nPowAveragingWindow=30;
	nPowTargetSpacingCDY=iT;  
	bnPowLimit=2**(256-40);
	AveragingWindowTimespan=nPowAveragingWindow * nPowTargetSpacingCDY;
	MinActualTimespan=(AveragingWindowTimespan * (100 - nPowMaxAdjustUp))/ 100;
	MaxActualTimespan= (AveragingWindowTimespan * (100 + nPowMaxAdjustDown)) / 100;

	if (nActualTimespan < MinActualTimespan):
	    nActualTimespan = MinActualTimespan
	if (nActualTimespan > MaxActualTimespan):
	    nActualTimespan = MaxActualTimespan;
	bnNew=bnAvg;
	bnNew = bnNew*nActualTimespan/ AveragingWindowTimespan;
	if (bnNew > bnPowLimit):
	    bnNew =bnPowLimit;  
	next_target=bnNew;
	next_Difficulty=2**(256-40)/next_target;  
	return next_Difficulty 
 

def main():
	time_start=time.time()
	AttackIn  = 0.85
	AttackOut = 1.5
	N = 40
	HRAttackerMulti = 20.0
   
	Lz = 2**40
	BaseD = 4.0
	T = 120.0
	HRworker = BaseD*Lz/120.0
	#print('hrworker',HRworker)	
	HRAttacker = HRAttackerMulti*HRworker
	n =  10**5
	#n = 500
	RndSeri = [0]*n
	for i in range(1,n):
		#RndSeri[i-1] = random.random()
		RndSeri[i-1] = random.uniform(0,1)
		#print 'rand',RndSeri[i-1]
	Dseri = [0.0]*n
	STseri = [0.0]*n
	HRSeri = [0.0]*n
	AttackSeri = [0]*n
	HRnow = HRworker
	Attackposition = 0
	ifattack = True
	for i in range(1,n):
		if i <= N:
			Dseri[i-1] = BaseD
			STseri[i-1] = randNum2SolveTimeFunc(HRnow,RndSeri[i-1],Dseri[i-1])
			AttackSeri[i-1] = 0
			HRSeri[i-1] = HRnow
			continue
		else:
			if ifattack:
                                #print 'dseri',Dseri[i-2],'  attackin',AttackIn*BaseD
				if Dseri[i-2]  <  AttackIn*BaseD and Attackposition == 0:
                                        #print 'cut in'
					Attackposition = 1
					HRnow  = HRAttacker + HRworker
				elif Dseri[i-2] > AttackOut*BaseD and Attackposition == 1:
					Attackposition = 0
					HRnow = HRworker
		next_Difficulty = getNextDiff_targetMean(Dseri,STseri,T,N,i)
		#next_Difficulty = getNextDiff_old(Dseri,STseri,T,N,i)
		Dseri[i-1] = next_Difficulty
		STseri[i-1] = randNum2SolveTimeFunc(HRnow,RndSeri[i-1],Dseri[i-1])
		HRSeri[i-1] = HRnow
		AttackSeri[i-1] = Attackposition
	STafterAttack = STseri[N:]
	AttackSeriAfter = AttackSeri[N:]
	WorkerCostTime = 0.0
	for i in range(N+1,n-N):
		WorkerCostTime = WorkerCostTime + STafterAttack[i-1]
	AttackerCostTime = 0.0
	for i in range(N+1,n-N):
		if AttackSeriAfter[i-1] > 0:
			AttackerCostTime = AttackerCostTime + STafterAttack[i-1]
	WorkerGetBlock = 0.0
	AttackerGetBlock = 0.0
	for i in range(N+1,n-N):
                #print 'attackseriafter',AttackSeriAfter[i-1]
		WorkerGetBlock = WorkerGetBlock + (1 - AttackSeriAfter[i-1]) + AttackSeriAfter[i-1]*HRworker/(HRworker + HRAttacker)
		AttackerGetBlock = AttackerGetBlock +  AttackSeriAfter[i-1]*HRAttacker/(HRworker + HRAttacker)
	
	WorkerSTperBlock = WorkerCostTime/WorkerGetBlock
	AttackerSTperBlock = AttackerCostTime/AttackerGetBlock
	stolenrate = WorkerSTperBlock*HRworker/(AttackerSTperBlock*HRAttacker)-1
	time_end=time.time()
	print('by time cost(s):',time_end-time_start)
	print('N=:',N)
	print('AttackIn=:',AttackIn) 
	print('AttackOut=:',AttackOut) 
	print('HRAttackerMulti=:',HRAttackerMulti) 
	print('stolenrate(%):',stolenrate*100) 
	print('meanST=',np.mean(STafterAttack))

if __name__ == '__main__':
    main()
