/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 */

#include <cstdlib>
#include <cstring>
#include <iostream>

#include "FaceIndex.hh"


int
main (int argc,
      char *argv[])
  {
    if (argc < 2 || !std::strcmp (argv[1], "-h") || !std::strcmp (argv[1], "--help"))
      {
        std::cerr << "\nUsage:  " << argv[0]
                  << " <gallery_txt_file> [<cluster_force=3.0>]"
                  << "\n\t<gallery_txt_file>  A file with .txt suffix "
                  << "containing paths to image files."
                  << "\n\t\t\t    The paths may be relative to the "
                  << "<gallery_txt_file> location."
                  << "\n\t<cluster_force>     A floating-point value between 0 "
                  << "and 10 specifying how"
                  << "\n\t\t\t    aggressive match clustering should be.  "
                  << "Defaults to 3.\n";
        return -1;
      }

    try
      {
        const char* corpusPath (argv[1]);


        AIDA::FaceIndexer indexer;
        std::string faceIndex (argc > 2
                               ? indexer.indexFaces (corpusPath,
                                                     std::atof (argv[2]))
                               : indexer.indexFaces (corpusPath));

        std::cerr << "\n\nGraph = \n";
        std::cout << faceIndex << std::endl;
      }
    catch (const std::exception& exc)
      {
        std::cerr << "\nCaught exception: " << exc.what () << std::endl;
      }
    return 0;
}

