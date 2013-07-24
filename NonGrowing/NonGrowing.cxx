/*=========================================================================

  Program:   Slicer4
  Language:  C++
  Module:    $HeadURL: $
  Date:      $Date: 2013-06-14 02:06PM -0400 (Fri, 14 JUN 2013) $
  Version:   $Revision: 67 $

  Copyright (c) Neuro Image Research and Analysis Lab, UNC-Chapel Hill All Rights Reserved.

  See License.txt or http://www.slicer.org/copyright/copyright.txt for details.

==========================================================================*/
#include <strstream> 
#include <string>
#include <stdio.h>
#include <stdlib.h>
#include <itksys/Glob.hxx>
//#include <dirent.h>

#include <vector>
#include <iostream>
#include <string.h>
#include <itksys/Glob.hxx>
#include <itksys/Process.h>
#include <cstring>
#include <fstream>
#include <sstream>
#include <itksys/SystemTools.hxx>
#include <time.h>

#include "vtkPolyDataReader.h"
#include "vtkPolyData.h"
#include "vtkPointSet.h"
#include "vtkDataSet.h"
#include "vtkCell.h"
#include "vtkCellArray.h"
#include "vtkPolyDataWriter.h"
 
#include <vtkMath.h>
#include <vtkMergePoints.h>
#include <vtkPointSource.h>
#include <vtkPoints.h>
#include <vtkPolyData.h>
#include <vtkDelaunay2D.h>
#include <vtkCellArray.h>
#include <vtkPolyData.h>
#include <vtkPolyDataWriter.h>
#include <vtkSmartPointer.h>

#include "NonGrowingCLP.h"

//#################################

#if defined(_MSC_VER)
#pragma warning ( disable : 4786 )
#endif

#ifdef __BORLANDC__
#define ITK_LEAN_AND_MEAN
#endif

// #include "itkOrientedImage.h"
#include "itkImageFileReader.h"
//#include "itkPluginUtilities.h"

void Run(std::vector<const char*> args, bool TimeOn)
{		
	cout << "Entered in the Run" << std::endl;
	//itk sys parameters
	int length;
	time_t start,end;
	time (&start);

	double timeout = 0.05;
	int result;
	char* dataitk = NULL;

	itksysProcess* gp = itksysProcess_New();
	itksysProcess_SetCommand(gp, &*args.begin());
	itksysProcess_SetOption(gp,itksysProcess_Option_HideWindow,1);
	itksysProcess_Execute(gp);
	cout << "Executed Process gp " << std::endl;
	while(int Value = itksysProcess_WaitForData(gp,&dataitk,&length,&timeout)) // wait for 1s
	{
		if ( ((Value == itksysProcess_Pipe_STDOUT) || (Value == itksysProcess_Pipe_STDERR)) && dataitk[0]=='D' )
		{
			std::strstream st;
			for(int i=0;i<length;i++) 	
			{
				st<<dataitk[i];
			}
			std::string dim=st.str();
		}
			if(TimeOn){
				time (&end);
				cout<<"(processing since "<<difftime (end,start)<<" seconds) \r";
				timeout = 0.05; 
			}  	
	}
	itksysProcess_WaitForExit(gp, 0);
	result = 1;
	switch(itksysProcess_GetState(gp))
	{
		case itksysProcess_State_Exited:
		{
			result = itksysProcess_GetExitValue(gp);
		} break;
		case itksysProcess_State_Error:
		{
			std::cerr<<"Error: Could not run " << args[0]<<":\n";
			std::cerr<<itksysProcess_GetErrorString(gp)<<"\n";
			std::cout<<"Error: Could not run " << args[0]<<":\n";
			std::cout<<itksysProcess_GetErrorString(gp)<<"\n";
		} break;
		case itksysProcess_State_Exception:
		{
			std::cerr<<"Error: "<<args[0]<<" terminated with an exception: "<<itksysProcess_GetExceptionString(gp)<<"\n";
			std::cout<<"Error: "<<args[0]<<" terminated with an exception: "<<itksysProcess_GetExceptionString(gp)<<"\n";
		} break;
		case itksysProcess_State_Starting:
		case itksysProcess_State_Executing:
		case itksysProcess_State_Expired:
		case itksysProcess_State_Killed:
		{
		// Should not get here.
		std::cerr<<"Unexpected ending state after running "<<args[0]<<std::endl;
		std::cout<<"Unexpected ending state after running "<<args[0]<<std::endl;
		} break;
	}
	itksysProcess_Delete(gp);  
}

int main(int argc, char * argv [])
{
  PARSE_ARGS;
  std::cout << "Running Registration Proccesses..." << std::endl;

/*Get Environment Variable*/

  std::string BFPath;
  BFPath = itksys::SystemTools::FindProgram("BRAINSFit"); //getenv("SLICER");
  std::string RV2Path;
  RV2Path = itksys::SystemTools::FindProgram("ResampleScalarVectorDWIVolume"); //getenv("SLICER");
  if(BFPath.empty()){
	cout << "The current BFPath path is: " << BFPath << std::endl;
	cout << "The current RV2Path path is: " << RV2Path << std::endl;
  }

  try{
	if (!movingMaskVolume.empty() && !fixedMaskVolume.empty()){
		std::vector<const char*> args;
	cout << "The current BFPath path is: " << BFPath << std::endl;
	cout << "The current RV2Path path is: " << RV2Path << std::endl;


		args.push_back(BFPath.c_str());
		args.push_back("--outputTransform");
		args.push_back(transformPath.c_str());
		args.push_back("--minimumStepLength 0.000001");
		args.push_back("--numberOfIterations 15000");
		args.push_back("--maskProcessingMode ROI");
		args.push_back("--useRigid");
		args.push_back("--movingBinaryVolume");
		args.push_back(movingMaskVolume.c_str());
		args.push_back("--fixedBinaryVolume");
		args.push_back(fixedMaskVolume.c_str());
		args.push_back("--movingVolume");
		args.push_back(movingVolume.c_str());	
		args.push_back("--fixedVolume");
		args.push_back(fixedVolume.c_str());
		args.push_back(0);
	
		cout << "Before Run" << std::endl;

		Run(args,0);

		cout << "After Run" << std::endl;
	}

	if(!segmentationOut.empty()){
		std::vector<const char*> args2;
		
		args2.push_back(RV2Path.c_str());
		args2.push_back("--interpolation nn");
		args2.push_back("--transformationFile");
		args2.push_back(transformPath.c_str());
		args2.push_back(segmentation.c_str());
		args2.push_back(segmentationOut.c_str());
		args2.push_back(0);
			
		Run(args2,0);
	}	
	
	if(!outputVolume.empty()){
		std::vector<const char*> args3;
			
		args3.push_back(RV2Path.c_str());
		args3.push_back("--interpolation nn");
		args3.push_back("--transformationFile");
		args3.push_back(transformPath.c_str());
		args3.push_back(movingVolume.c_str());
		args3.push_back(outputVolume.c_str());
		args3.push_back(0);
		
		Run(args3,0);
	}

  	typedef itk::Image<short,3> ImageType;
  	typedef itk::ImageFileReader<ImageType> ReaderType;

	ReaderType::Pointer reader = ReaderType::New();

	reader->SetFileName( segmentationOut.c_str() );
	reader->ReleaseDataFlagOn();
	reader->Update();
  }
  catch(itk::ExceptionObject &excep){
	std::cerr << argv[0] << ":exception caught!" << std::endl;
	return EXIT_FAILURE;
  }

  return EXIT_SUCCESS;
}
