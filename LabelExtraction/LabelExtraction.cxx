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

#include "LabelExtractionCLP.h"

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

#include <itkBinaryThresholdImageFilter.h> 
#include <itkCastImageFilter.h>

enum { ImageDimension = 3 };
typedef short                                                     ShortPixelType;
typedef itk::Image<int, ImageDimension>                           ImageType;
typedef itk::Image<ShortPixelType,ImageDimension>                 ShortImageType;
typedef itk::ImageFileReader< ImageType >                         VolumeReaderType;
typedef itk::BinaryThresholdImageFilter< ImageType , ImageType >  threshFilterType;
typedef ImageType::Pointer                                        ImagePointer;
typedef itk::ImageBase< 3 >                                       ImageBaseType ;
typedef itk::ImageFileWriter< ShortImageType >                    ShortVolumeWriterType;
typedef itk::CastImageFilter< ImageType,  ShortImageType >        castShortFilterType; 
typedef itksys_VA_LIST::basic_string<char>                        string;


int main(int argc, char * argv [])
{
  PARSE_ARGS;
  std::cout << "Running Extraction Proccesses..." << std::endl;
 
  try{	
        const char *inputFileName = inputVolume.c_str();                
	const char *outputFileName = outputVolume.c_str();   
	char *outbase    = NULL;
	char * base_string;
	itksys_VA_LIST::string outFileName ("dummy");

	if (!outbase) { 
	  if (!outputFileName) {
	    base_string = strdup(inputFileName);
	  } else {
	    base_string = strdup(outputFileName);
	  }
	} else {
	  base_string = outbase;
	}

	int extractLabel = atoi(label.c_str());
	ImagePointer inputImage ;
	ImageBaseType::Pointer inputBaseImage ;

	// Read image
	VolumeReaderType::Pointer imageReader = VolumeReaderType::New();
	imageReader->SetFileName(inputFileName) ;
	try{
	    imageReader->Update();
	}
	catch (itk::ExceptionObject & err){
	    cerr << "ExceptionObject caught!" << endl;
	    cerr << err << endl;
	    return EXIT_FAILURE;	
	}    
	inputImage = imageReader->GetOutput();
	inputBaseImage = inputImage ;	

	// extractionLabel
	outFileName.erase();
	outFileName.append(base_string);
	
	if (true) cout << "extracting object " << extractLabel << endl; 
    
	threshFilterType::Pointer threshFilter = threshFilterType::New();
	threshFilter->SetInput(inputImage);
	threshFilter->SetLowerThreshold(extractLabel);
	threshFilter->SetUpperThreshold(extractLabel);
	threshFilter->SetOutsideValue (0); //BGVAL
	threshFilter->SetInsideValue (1);  //FGVAL
	try {
	  threshFilter->Update();
	}
	catch (itk::ExceptionObject & err) {
	  cerr << "ExceptionObject caught!" << endl;
	  cerr << err << endl;
	  return EXIT_FAILURE;	
	}        
	inputImage = threshFilter->GetOutput();

	outFileName.append(".gipl");

	if (outputFileName) {
	  outFileName = string(outputFileName);
	}

	castShortFilterType::Pointer castFilter = castShortFilterType::New();
	castFilter->SetInput(inputImage);
	try {
	  castFilter->Update();
	}
	catch (itk::ExceptionObject & err) {
	  cerr << "ExceptionObject caught!" << endl;
	  cerr << err << endl;
	  return EXIT_FAILURE;	
	}
	
	ShortVolumeWriterType::Pointer writer = ShortVolumeWriterType::New();
	writer->SetFileName(outFileName.c_str()); 
        if (true) writer->UseCompressionOn();
	writer->SetInput(castFilter->GetOutput());
	writer->Write();

	typedef itk::Image<short,3> ImageType;
	typedef itk::ImageFileReader<ImageType> ReaderType;
	
	ReaderType::Pointer reader = ReaderType::New();
	
	reader->SetFileName( outputVolume.c_str() );
	reader->ReleaseDataFlagOn();
	
	reader->Update();
	
  }
  catch(itk::ExceptionObject &excep){
	std::cerr << argv[0] << ":exception caught!" << std::endl;
	return EXIT_FAILURE;
  }

  return EXIT_SUCCESS;
}
