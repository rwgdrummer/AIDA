////============================================================================
////
////    FILE:           FaceIndex.hh
////
////    DESCRIPTION:    TODO description.
////
////    AUTHOR(S):      scott		scott@partech.com
////
////
////    HISTORY:
////
////      DATE          AUTHOR          COMMENTS
////	  ------------  --------        --------
////      Oct 23, 2018	scott		Created.
////
////========================================================================////
////                                                                        ////
////    (c) Copyright 2018 PAR Government Systems Corporation.              ////
////                                                                        ////
////========================================================================////

#ifndef	AIDA_FACE_INDEX_HH_INCLUDED
#define	AIDA_FACE_INDEX_HH_INCLUDED

////========================================================================////
////                                                                        ////
////    INCLUDES AND MACROS                                                 ////
////                                                                        ////
////========================================================================////


#include <memory>
#include <string>


////========================================================================////
////                                                                        ////
////    FORWARD DECLARATIONS                                                ////
////                                                                        ////
////========================================================================////

////========================================================================////
////                                                                        ////
////    TYPE DEFINITIONS                                                    ////
////                                                                        ////
////========================================================================////


namespace AIDA                          // Open the AIDA namespace.
{


///=============================================================================
///
///  class FaceIndexer
///
///     Performs face detection in a set of image files, producing a
///     JSON-formatted graph of clusters of similar faces.
///
///     The graph has the form:
///
///  {
///      "nodes": [
///          {
///              "ID": "<64-bit numeric hash>",
///              "imagePath": "<path_to_image>",
///              "faceRect": [ <x>, <y>, <w>, <h> ]
///          },
///          ...,
///      ],
///      "edges": [
///          {
///              "IDs": [ "<64-bit numeric hash>", "<64-bit numeric hash>" ],
///              "similarity": <float>
///          },
///          ...,
///      ],
///  }
///
///
///=============================================================================


class FaceIndexer
  {
                                        //====================================//
  public:                               //                      PUBLIC        //
                                        //====================================//


    //
    // Initializes FaceIndexer for face detection processing.  OpenBR_Root is
    // the path to the OpenBR SDK, if it is not already located in $PATH.
    // Alternatively, it may be provided by setting an OPENBR_ROOT environment
    // variable.
    //
    FaceIndexer (const std::string& OpenBR_Root = { });

    ~FaceIndexer ();

    //
    // Perform face detection from images listed in the file found at
    // corpusFilePath (which must have a .txt suffix).  Returns a JSON-formatted
    // graph of clusters of similar faces.
    //
    // corpusFilePath must end in .txt.
    // clusterForce sets how aggressively clustering is performed.  Recommended
    // value range is [0..10].
    //
    std::string
    indexFaces (const std::string& corpusFilePath,
                float clusterForce = 3);


                                        //====================================//
  protected:                            //                      PROTECTED     //
                                        //====================================//

                                        //====================================//
  private:                              //                      PRIVATE       //
                                        //====================================//


    //==================================
    //  PRIVATE NESTED TYPES
    //==================================


    class Impl;


    //==================================
    //  PRIVATE REPRESENTATION
    //==================================


    std::unique_ptr<Impl> impl;
  };


}                                       // Close the AIDA namespace.


////========================================================================////
////                                                                        ////
////    EXTERN DECLARATIONS                                                 ////
////                                                                        ////
////========================================================================////

////========================================================================////
////                                                                        ////
////    PUBLIC INLINE DEFINITIONS                                           ////
////                                                                        ////
////========================================================================////

////========================================================================////
////                                                                        ////
////    PROTECTED INLINE DEFINITIONS                                        ////
////                                                                        ////
////========================================================================////


#endif  // #ifndef AIDA_FACE_INDEX_HH_INCLUDED
