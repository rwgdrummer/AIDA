#include <functional>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include <openbr/openbr.h>


namespace                               // Open unnamed namespace.
{


std::string
getDirPath (const std::string& filePath)
  {
    std::string::size_type slash (filePath.rfind ("/"));

    return slash > 0 ? filePath.substr (0, slash + 1) : std::string ("./");
  }


std::string
getFileName (const std::string& filePath)
  {
    std::string::size_type slash (filePath.rfind ("/"));
    std::string::size_type dot (filePath.rfind ("."));

    return filePath.substr (slash + 1, dot - slash - 1);
  }


std::string
makeDirPath (std::string path)
  {
    if (path.empty ())
      {
        return "./";
      }
    else if (path[0] != '.' && path[0] != '/')
      {
        path = "./" + path;
      }

    return path[path.size () - 1] == '/' ? path : path + "/";
  }


}                                       // Close unnamed namespace.


int
main (int argc,
      char *argv[])
  {
    if (argc < 1)
      {
        std::cerr << "\nUsage: " << argv[0]
                                 << " <input_file_path>"
                                 << " [<output_dir_path=input_file_dir>]"
                                 << " [<cluster_aggression=3.0>]";
        return -1;
      }

    std::string inputPath (argv[1]);
    std::string outputDir (argc > 2
                           ? makeDirPath (argv[2])
                           : getDirPath (inputPath));
    float clusterForce (argc > 3 ? std::atof (argv[3]) : 3.0);
    char* OpenBR_SDK (std::getenv ("OPENBR_ROOT"));

    std::cout << "\nProcessing images listed in " << inputPath
              << "\nSaving results in directory " << outputDir
              << "\nCluster aggression = " << clusterForce
              << std::endl;
    br_initialize (argc, argv, OpenBR_SDK ? OpenBR_SDK : "");

    //
    // Equivalent to 'Globals-><mumble> = "<yadayada>";' in C++ API.
    //
    br_set_property ("algorithm", "FaceRecognition");
    br_set_property ("enrollAll", "true");      // Enroll 0 or more faces.

    //
    // Enroll galleries, don't re-enroll if they already exist (cache).
    //
    std::string inputName (getFileName (inputPath));
    std::string outputBase (outputDir + inputName);
    std::string galleryPath (outputBase + ".gal");

    br_enroll (inputPath.c_str (),
               (galleryPath + "[cache]").c_str ());

    //
    // Compare galleries and store result in a binary similarity matrix.
    //
    std::ostringstream strm;

    strm << "_Clusters"
         << std::setw (2) << std::setfill ('0') << std::setprecision (2)
         << clusterForce
         << ".csv";

    std::string matrixPath (outputBase + "Compare.mtx");
    const char* matrix (matrixPath.c_str ());
    std::string clustersPath (outputBase + strm.str ());

    br_compare (galleryPath.c_str (), galleryPath.c_str (), matrixPath.c_str ());
    br_cluster (1, &matrix, clusterForce, clustersPath.c_str ());

    //
    // Save the gallery and output data in more convenient formats.
    //
    br_convert ("Output", matrixPath.c_str (),
                (outputBase + "Compare.csv").c_str ());
    br_convert ("Gallery", galleryPath.c_str (),
                (outputBase + ".csv").c_str ());
    br_convert ("Gallery", galleryPath.c_str (),
                (outputBase + ".flat").c_str ());

    br_finalize ();
    return 0;
}
