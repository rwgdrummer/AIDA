////============================================================================
////
////    FILE:           FaceIndex.cc
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

////========================================================================////
////                                                                        ////
////    INCLUDES AND MACROS                                                 ////
////                                                                        ////
////========================================================================////


#include "FaceIndex.hh"

#include <cstdlib>
#include <functional>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <vector>

#include <openbr/openbr_plugin.h>
#include <openbr/core/cluster.h>
#include <openbr/core/opencvutils.h>

#include "opencv2/core.hpp"
#include "opencv2/core/persistence.hpp"


////========================================================================////
////                                                                        ////
////    USING DIRECTIVES AND DECLARATIONS                                   ////
////                                                                        ////
////========================================================================////

////========================================================================////
////                                                                        ////
////    EXTERN DECLARATIONS                                                 ////
////                                                                        ////
////========================================================================////

////========================================================================////
////                                                                        ////
////    FILE-SCOPED TYPE DEFINITIONS                                        ////
////                                                                        ////
////========================================================================////


namespace                               // Open unnamed namespace.
{


struct BR_ContextInitializer
  {
    BR_ContextInitializer (std::string OpenBR_SDK)
      {
        bool checkEnv (OpenBR_SDK.empty ());

        if (checkEnv)
          {
            const char* env (std::getenv ("OPENBR_ROOT"));

            if (env)
              {
                OpenBR_SDK = env;
              }
          }

        int argc (0);

        br::Context::initialize (argc, nullptr, OpenBR_SDK.c_str (), false);
        if (!br::Globals)
          {
            std::ostringstream errStrm;

            errStrm << "OpenBR context initialization failed.  ";
            if (OpenBR_SDK.empty ())
              {
                errStrm << "OpenBR_Root not provided and OPENBR_ROOT not set.";
              }
            else
              {
                errStrm << "Check value of "
                        << (checkEnv ? "OPENBR_ROOT" : "OpenBR_Root")
                        << "(" << OpenBR_SDK << ").";
              }

            throw std::runtime_error (errStrm.str ());
          }
      }

    ~BR_ContextInitializer ()
      { br::Context::finalize (); }
  };


using ID_Type = std::size_t;
using NodeID_Map = std::map<unsigned int, ID_Type>;


struct Node
  {
    Node (std::string imagePath,
          cv::Rect faceRect);

    std::string imagePath;
    cv::Rect faceRect;
    ID_Type ID;
  };


struct Edge
  {
    Edge (ID_Type n0,
          ID_Type n1,
          float score)
      : node0 (n0),
        node1 (n1),
        score (score)
      { }

    ID_Type node0;
    ID_Type node1;
    float score;
  };


struct Graph
  {
    Graph (const br::FileList& files)
      : files (files)
      {
        nodes.reserve (files.size ());
        edges.reserve (files.size ());
      }

    void
    addEdge (unsigned int node0,
             unsigned int node1,
             float score)
      { edges.emplace_back (nodeIDs.at (node0), nodeIDs.at (node1), score); }

    void
    addNode (unsigned int nodeID)
      {
        const br::File& file (files[nodeID]);

        if (!file.contains ("FrontalFace"))
          {
            std::ostringstream strm;

            strm << "Node " << nodeID << " has no FrontalFace!";
            throw std::invalid_argument (strm.str ());
          }

        Node node (file.name.toStdString (),
                   OpenCVUtils::toRect (file.get<QRectF> ("FrontalFace")));

        nodeIDs[nodeID] = node.ID;
        nodes.push_back (node);
      }

    const br::FileList& files;
    std::vector<Node> nodes;
    std::vector<Edge> edges;
    NodeID_Map nodeIDs;
  };


}                                       // Close unnamed namespace.


////========================================================================////
////                                                                        ////
////    EXTERN VARIABLE DEFINITIONS                                         ////
////                                                                        ////
////========================================================================////

////========================================================================////
////                                                                        ////
////    FILE-SCOPED VARIABLE DEFINITIONS                                    ////
////                                                                        ////
////========================================================================////

namespace                               // Open unnamed namespace.
{


}                                       // Close unnamed namespace.

////========================================================================////
////                                                                        ////
////    FILE-SCOPED FUNCTION DEFINITIONS                                    ////
////                                                                        ////
////========================================================================////


namespace std                           // Open std namespace.
{


template<>
struct hash<cv::Rect>
  {
    using argument_type = cv::Rect;
    using result_type = size_t;

    result_type
    operator() (const argument_type& val)
        const noexcept
      {
        static const std::size_t magic (0x9E3779B97F4A7C15);
        std::hash<cv::Rect::value_type> hash;
        result_type result (hash (val.x) + magic);

        result ^= hash (val.y) + magic + (result << 6) + (result >> 2);
        result ^= hash (val.width) + magic + (result << 6) + (result >> 2);
        result ^= hash (val.height) + magic + (result << 6) + (result >> 2);
        return result;
        }
    };


template<>
struct hash<Node>
  {
    using argument_type = Node;
    using result_type = size_t;

    result_type
    operator() (const argument_type& val)
        const noexcept
      {
        result_type result (hash<string> { } (val.imagePath)
                            + 0x9E3779B97F4A7C15);

        result ^= hash<cv::Rect> { } (val.faceRect)
                + 0x9E3779B97F4A7C15 + (result << 6) + (result >> 2);
        return result;
        }
    };


}                                       // Close std namespace.


namespace                               // Open unnamed namespace.
{


inline
Node::Node (std::string path,
            cv::Rect rect)
  : imagePath (std::move (path)),
    faceRect (std::move (rect)),
    ID (std::hash<Node> () (*this))
  { }


Graph
buildGraph (const br::FileList& files,
            const br::Clusters& clusters,
            const cv::Mat& scores)
  {
    Graph graph (files);
    std::map<std::size_t, std::size_t> clusterSizes;

    for (const auto& cluster : clusters)
      {
        ++clusterSizes[cluster.size ()];

        for (unsigned int i (0); i < cluster.size (); ++i)
          {
            graph.addNode (cluster[i]);
          }
        for (unsigned int i (0); i < cluster.size (); ++i)
          {
            for (unsigned int j (i + 1); j < cluster.size (); ++j)
              {
                graph.addEdge (cluster[i], cluster[j],
                               scores.at<float> (cluster[i], cluster[j]));
              }
          }
      }
    std::cerr << "\nFound " << clusters.size () << " clusters:"
              << "\nSize    Count\n====    =====";
    for (const auto& elem : clusterSizes)
      {
        std::cerr << "\n" << std::setw (4) << elem.first
                          << std::setw (9) << elem.second;
      }

    return graph;
  }


///=============================================================================
///
///  FUNCTION:          getDirPath (const std::string& filePath)
///
///  PROCESSING:        Returns everything before the last slash in the supplied
///                     filePath.  If there is no slash, returns ".".
///
///=============================================================================



std::string
getDirPath (const std::string& filePath)
  {
    std::string::size_type slash (filePath.rfind ("/"));

    return slash >= 0 ? filePath.substr (0, slash) : std::string (".");
  }


#if 0
void
printEdge (unsigned int n0,
           unsigned int n1,
           float score)
  {
    std::cerr << "\nEdge:       [ " << n0 << ", " << n1 << " ] = " << score;
  }


void
printNode (const br::FileList& files,
           unsigned int node)
  {
    QRectF faceRect (files[node].get<QRectF> ("FrontalFace"));
    std::cerr << "\nNode:       " << node
              << "\n  Image:    " << files[node].name.toStdString ()
              << "\n  FaceRect: [ " << faceRect.x () << ", "
                                    << faceRect.y ()<< ", "
                                    << faceRect.width () << ", "
                                    << faceRect.height () << " ]";
  }

void
printTemplate (const br::Template &t)
{
    std::cout << "\nTemplate metadata for " << t.file.fileName ().toStdString ();
    for (auto elem : t.file.localMetadata ().toStdMap ())
      { qDebug () << elem.first << "= " << elem.second; }
}


void
printTemplate (const br::TemplateList& tList)
  {
    for (const auto& item : tList)
      { printTemplate (item); }
  }
#endif


cv::FileStorage&
operator<< (cv::FileStorage& fs,
            const Edge& edge)
  {
    //
    // OpenCV's FileStorage supports only int, float, double, string, no size_t.
    //
    std::ostringstream strm0;
    std::ostringstream strm1;

    strm0 << edge.node0;
    strm1 << edge.node1;
    return fs << "{"
              << "IDs" << "[:" << strm0.str () << strm1.str () << "]"
              << "similarity" << edge.score
              << "}";
  }


cv::FileStorage&
operator<< (cv::FileStorage& fs,
            const Node& node)
  {
    //
    // OpenCV's FileStorage supports only int, float, double, string, no size_t.
    //
    std::ostringstream strm;

    strm << node.ID;
    return fs << "{"
              << "ID" << strm.str ()
              << "imagePath" << node.imagePath
              << "faceRect" << node.faceRect
              << "}";
  }


template <typename T>
cv::FileStorage&
operator<< (cv::FileStorage& fs,
            const std::vector<T>& elems)
  {
    fs << "[";
    for (const auto& elem : elems)
      { fs << elem; }
    return fs << "]";
  }


cv::FileStorage&
operator<< (cv::FileStorage& fs,
            const Graph& graph)
  { return fs << "nodes" << graph.nodes << "edges" << graph.edges; }


}                                       // Close unnamed namespace.


////========================================================================////
////                                                                        ////
////    EXTERN FUNCTION DEFINITIONS                                         ////
////                                                                        ////
////========================================================================////

////========================================================================////
////                                                                        ////
////    PRIVATE INLINE MEMBER FUNCTION DEFINITIONS                          ////
////                                                                        ////
////========================================================================////


namespace AIDA                          // Open AIDA namespace.
{


///=============================================================================
///
///  class FaceIndexer::Impl
///
///     FaceIndexer Pimpl used to keep FaceIndexer interface Qt-free.
///
///=============================================================================


class FaceIndexer::Impl
  {
                                        //====================================//
  public:                               //                      PUBLIC        //
                                        //====================================//


    Impl ()
      : transform (br::Transform::fromAlgorithm ("FaceRecognition")),
        distance (br::Distance::fromAlgorithm ("FaceRecognition"))
      { }


    //==================================
    //  PUBLIC REPRESENTATION
    //==================================


    QSharedPointer<br::Transform> transform;
    QSharedPointer<br::Distance> distance;
  };


}                                       // Close AIDA namespace.


////========================================================================////
////                                                                        ////
////    PUBLIC MEMBER FUNCTION DEFINITIONS                                  ////
////                                                                        ////
////========================================================================////


namespace AIDA                          // Open AIDA namespace.
{


FaceIndexer::FaceIndexer (const std::string& OpenBR_Root)
  {
    static BR_ContextInitializer init (OpenBR_Root);

    impl.reset (new Impl);              // Must occur after BR initialization.
  }


FaceIndexer::~FaceIndexer ()
  { }


std::string
FaceIndexer::indexFaces (const std::string& corpusFilePath,
                         float clusterForce)    // Defaults to 5.
  {
    //
    // Need to be able to load corpus as a br::Gallery.
    //
    if (corpusFilePath.size () < 4
        || corpusFilePath.rfind (".txt") != corpusFilePath.size () - 4)
      {
        throw std::invalid_argument ("Supplied corpusFilePath lacks required "
                                     ".txt suffix.");
      }

    //
    // Permit relative paths in the corpusFilePath contents.
    //
    br::Globals->path = getDirPath (corpusFilePath).c_str ();
    br::Globals->verbose = true;
    br::Globals->enrollAll = true;      // Enroll 0 or more faces per image.

    br::TemplateList templates
        (br::TemplateList::fromGallery (corpusFilePath.c_str ()));

    templates >> *impl->transform;

    br::FileList files (templates.files ());
    QScopedPointer<br::MatrixOutput> scores
        (br::MatrixOutput::make (files, files));
    QList<cv::Mat> mats;

    if (files.empty ())
      {
        std::cerr << "\nNo faces found in files listed in " << corpusFilePath;
        return "{ }";
      }
    std::cerr << "\nLooking for matches among " << files.size () << " faces.\n";

    impl->distance->compare (templates, templates, scores.data ());
    mats.append (scores->data);

    Graph graph (buildGraph (files,
                             br::ClusterSimmat (mats, clusterForce),
                             scores->data));
    cv::FileStorage graphStrm ("", cv::FileStorage::WRITE
                                   | cv::FileStorage::MEMORY
                                   | cv::FileStorage::FORMAT_JSON);

    if (!graphStrm.isOpened ())
      {
        throw std::runtime_error ("Failed to open cv::FileStorage JSON stream.");
      }

    return (graphStrm << graph).releaseAndGetString ();
  }


}                                       // Close AIDA namespace.


////========================================================================////
////                                                                        ////
////    PROTECTED MEMBER FUNCTION DEFINITIONS                               ////
////                                                                        ////
////========================================================================////

////========================================================================////
////                                                                        ////
////    PRIVATE MEMBER FUNCTION DEFINITIONS                                 ////
////                                                                        ////
////========================================================================////

