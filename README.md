CMFreg
======

Cranio-Maxillofacial registration

For assessment of overall facial changes, cranial base segmented models are only used to mask anatomic structures that change with growth and treatment. The registration procedures actually compare voxel by voxel of gray-level CBCT images, containing only the cranial base, to calculate rotation and translation parameters between the 2 images. Cranial base registration yields information of facial displacements relative to the cranial base. For subjects in whom cranial base growth is complete, registration is done using the gray level CBCT datasets of the whole cranial base ( Nongrowing registration module). The larger the number of voxels used for the registration, the more robust the registration is. For this reason, for adult patients the whole cranial base “mask CBCT” is used for registration. For growing patients ( Growing registration module), the registration includes two steps in the same module: in the first, an initial head alignment is done using the whole cranial base, and then a finer registration is performed at the stable structure on the anterior cranial base.
For assessment of localized facial changes, such as mandibular or maxillary growth or bone remodeling of the mandibular condyle or tooth movement, specific anatomic regions can be used to create localized masks and aid regional superimpositions. The challenge in regional superimpositions is to determine which structures offer stable reference for registration.

The CMFregistration modules also include the following functionalities:

* Downsize image: for high resolution image files with large size, downsizing facilitates image analysis, making it more robust and saving computing processing time. In this tool, any voxel size can be entered to resample the volume.

* Label extraction and Label addition: segmentation files can be modified to extract or add a anatomic region of interest into a new file.

* Mask creation: segmentation files are used to : 1: generate CBCT files that can be used to mask anatomic regions that changed with growth and treatment ; or 2: generate a CBCT file that contains only the anatomic region of interest for regional superimpositions.

https://sites.google.com/a/umich.edu/dentistry-image-computing/Clinical-Applications/3d-registration---longitudinal-and-across-subjects

http://www.slicer.org/slicerWiki/index.php/Documentation/4.4/Extensions/CMFreg

## License

It is covered by the Apache License, Version 2.0:

http://www.apache.org/licenses/LICENSE-2.0

The license file was added at revision 7bc7dc7 on 2020-12-10, but you may consider that the license applies to all prior revisions as well.
