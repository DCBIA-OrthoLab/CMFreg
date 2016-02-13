/*=========================================================================

  Program:   Slicer4
  Language:  C++
  Module:    $HeadURL: $
  Date:      $Date: 2013-06-14 02:06PM -0400 (Fri, 14 JUN 2013) $
  Version:   $Revision: 67 $

  Copyright (c) Neuro Image Research and Analysis Lab, UNC-Chapel Hill All Rights Reserved.

  See License.txt or http://www.slicer.org/copyright/copyright.txt for details.

==========================================================================*/
#include <sstream>
#include <string>
#include <stdio.h>
#include <stdlib.h>
#include <itksys/Glob.hxx>

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

#include <vtkSlicerConfigure.h>

#include "LabelAdditionCLP.h"

//#################################

#if defined(_MSC_VER)
#pragma warning ( disable : 4786 )
#endif

#ifdef __BORLANDC__
#define ITK_LEAN_AND_MEAN
#endif

#include "itkImageFileReader.h"
#include "itkImageFileWriter.h"

#include "itkBSplineInterpolateImageFunction.h"
#include "itkResampleImageFilter.h"
#include "itkConstrainedValueAdditionImageFilter.h"

//#include "itkPluginUtilities.h"

void Run(std::vector<const char*> args, bool TimeOn)
{		
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
	while(int Value = itksysProcess_WaitForData(gp,&dataitk,&length,&timeout)) // wait for 1s
	{
		if ( ((Value == itksysProcess_Pipe_STDOUT) || (Value == itksysProcess_Pipe_STDERR)) && dataitk[0]=='D' )
		{
			std::stringstream st;
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
  std::cout << "Running Combination Proccesses..." << std::endl;

/*Get Environment Variable*/
  std::vector<std::string> userPaths;

#if defined(__APPLE__)
  // on Mac, slicer does not provide a PATH variable that includes the built-in CLIs
  // so we add it here.
  std::string slicerHome;
  if (itksys::SystemTools::GetEnv("SLICER_HOME", slicerHome))
    {
    // Slicer_CLIMODULES_BIN_DIR is defined in vtkSlicerConfigure.h which is configured in the inner-build
    // directory of Slicer
    userPaths.push_back( slicerHome + "/" + Slicer_CLIMODULES_BIN_DIR  ) ;
    std::cout<<"Additional Paths: " << slicerHome + "/" + Slicer_CLIMODULES_BIN_DIR << std::endl ;
    }

#endif

  std::string IMPath;
  IMPath = itksys::SystemTools::FindProgram("ImageLabelCombine", userPaths);
  std::cout << "Path to ImageLabelCombine executable: " << IMPath << std::endl ;

/*Endvironment Variable*/

  try{
	std::vector<const char*> args;

	args.push_back(IMPath.c_str());
	args.push_back(inputVolumeA.c_str());
	args.push_back(inputVolumeB.c_str());
	args.push_back(outputVolume.c_str());
	args.push_back(0);

	Run(args,0);

	typedef itk::Image<short,3> ImageType;
	typedef itk::ImageFileReader<ImageType> ReaderType;
	
	ReaderType::Pointer reader = ReaderType::New();
	
	reader->SetFileName( outputVolume.c_str() );
	reader->ReleaseDataFlagOn();
	
	reader->Update();
	
  }
  catch(itk::ExceptionObject &excep){
	std::cout << excep << ":exception caught!" << std::endl;

	return EXIT_FAILURE;
  }

  return EXIT_SUCCESS;
}
