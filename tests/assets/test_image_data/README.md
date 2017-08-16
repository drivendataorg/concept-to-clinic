# DICOM-images for testing

This folder contains DICOM image files for testing purposes.

## Folder structure

DICOM-datasets are organized in a folder structure. The uppermost folder represents
the patient (e.g. `LIDC_IDRI-0001`). This folder contains folders representing the single 
studies that were performed on the patient (e.g. `1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178`).
The study-folders again contain folders representing one or multiple image series 
(e.g. `1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192`). A series consists 
of one or multiple `*.dcm`-files. Each file represents one slice in z-direction. Additionally 
an `*.xml`-file might also be in the series folder. It contains annotations like nodule position 
added during earlier analysis.

````
|- full
|   |
|   |- Dataset/Patient #1 (e.g. LIDC_IDRI-0001)
|   |       |
|   |       |- Study #1 (e.g. 1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178)
|   |       |   |
|   |       |   |- Series #1 (e.g. 1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192)
|   |       |   |   |
|   |       |   |   |- dcm-file #1 (e.g. 000001.dcm)
|   |       |   |   |
|   |       |   |   |- annotation-file (e.g. 069.xml)
|   |       |   |
|   |       |
|   |       |- Study #2
        ...
|-small
|   |
|   |- Dataset/Patient #1 (e.g. LIDC_IDRI-0001)
|   |       |
|   |       |- Study #1 (e.g. 1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178)
|   |       |   |
|   |       |   |- Series #1 (e.g. 1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192)
|   |       |   |   |
|   |       |   |   |- File #1 (e.g. -95.00000.dcm)
|   |       |   |
|   |       |
|   |       |- Study #2
        ...

````

## Full vs. small

The small dataset was derived from the full dataset with the purpose of providing smaller
and therefore faster test data. The folder structure is exactly the same as for the full 
dataset, but the file names differ in that they are no non-consecutive ids, but the distance 
given in the DICOM metadata. This change makes it easier to identify their position in the z-stack.
