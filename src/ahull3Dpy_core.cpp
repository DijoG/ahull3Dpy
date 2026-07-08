// src/ahull3Dpy_core.cpp
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Delaunay_triangulation_3.h>
#include <CGAL/Fixed_alpha_shape_vertex_base_3.h>
#include <CGAL/Fixed_alpha_shape_cell_base_3.h>
#include <CGAL/Fixed_alpha_shape_3.h>
#include <CGAL/Tetrahedron_3.h>
#include <map>
#include <list>
#include <limits>
#include <vector>
#include <cmath>

namespace py = pybind11;

typedef CGAL::Exact_predicates_inexact_constructions_kernel K;
typedef K::Point_3 Point3;
typedef CGAL::Fixed_alpha_shape_vertex_base_3<K> Vb;
typedef CGAL::Fixed_alpha_shape_cell_base_3<K> Cb;
typedef CGAL::Triangulation_data_structure_3<Vb, Cb> Tds;
typedef CGAL::Delaunay_triangulation_3<K, Tds> Delaunay;
typedef CGAL::Fixed_alpha_shape_3<Delaunay> Fixed_alpha_shape_3;
typedef Fixed_alpha_shape_3::Facet Facet;
typedef Fixed_alpha_shape_3::Cell_handle Cell_handle;
typedef K::Tetrahedron_3 Tetrahedron;

struct Point3Comparator {
    bool operator()(const Point3& a, const Point3& b) const {
        const double eps = 1e-9;
        if (std::abs(a.x() - b.x()) > eps) return a.x() < b.x();
        if (std::abs(a.y() - b.y()) > eps) return a.y() < b.y();
        if (std::abs(a.z() - b.z()) > eps) return a.z() < b.z();
        return false;
    }
};

std::tuple<py::array_t<double>, py::array_t<double>, std::map<std::string, double>>
fas_cpp_with_labels(py::array_t<double> pts, double alpha, 
                    py::array_t<double> input_labels, bool volume) {
    
    auto buf_pts = pts.request();
    auto buf_labels = input_labels.request();
    
    if (buf_pts.ndim != 2 || buf_pts.shape[1] != 3) {
        throw std::runtime_error("Points must be Nx3 matrix");
    }
    
    const int npoints = buf_pts.shape[0];
    double* ptr_pts = static_cast<double*>(buf_pts.ptr);
    double* ptr_labels = static_cast<double*>(buf_labels.ptr);
    
    // Store points and build label map
    std::list<Point3> points_list;
    std::map<Point3, double, Point3Comparator> point_to_label;
    
    for(int i = 0; i < npoints; i++) {
        Point3 p(ptr_pts[i*3], ptr_pts[i*3+1], ptr_pts[i*3+2]);
        points_list.push_back(p);
        point_to_label[p] = ptr_labels[i];
    }
    
    // Compute alpha shape
    Fixed_alpha_shape_3 as(points_list.begin(), points_list.end(), alpha);
    
    // Get the facets
    std::list<Facet> facets;
    as.get_alpha_shape_facets(std::back_inserter(facets),
                              Fixed_alpha_shape_3::REGULAR);
    as.get_alpha_shape_facets(std::back_inserter(facets),
                              Fixed_alpha_shape_3::SINGULAR);
    
    const int nfacets = facets.size();
    
    // Check if any facets found
    if (nfacets == 0) {
        py::print("Warning: No facets found in alpha shape");
        return std::make_tuple(
            py::array_t<double>({0, 3}),
            py::array_t<double>(0),
            std::map<std::string, double>()
        );
    }
    
    // Output arrays - each facet has 3 vertices, each vertex has 3 coords
    std::vector<double> vertices;
    std::vector<double> vertex_labels;
    vertices.reserve(nfacets * 9);  // 3 vertices * 3 coords
    vertex_labels.reserve(nfacets * 3);  // 3 labels per facet
    
    std::list<Facet>::iterator it_facet;
    
    for(it_facet = facets.begin(); it_facet != facets.end(); it_facet++) {
        Facet facet = *it_facet;
        
        // to have a consistent orientation, always consider an exterior cell
        if(as.classify(facet.first) != Fixed_alpha_shape_3::EXTERIOR) {
            facet = as.mirror_facet(facet);
        }
        
        int indices[3] = {
            (facet.second + 1) % 4,
            (facet.second + 2) % 4,
            (facet.second + 3) % 4,
        };
        
        // needed to get a consistent orientation
        if(facet.second % 2 == 0) {
            std::swap(indices[0], indices[1]);
        }
        
        const Point3 v1 = facet.first->vertex(indices[0])->point();
        const Point3 v2 = facet.first->vertex(indices[1])->point();
        const Point3 v3 = facet.first->vertex(indices[2])->point();
        
        // Store vertices (as 3 separate vertices, not triangles)
        auto assign_label = [&](const Point3& p) -> double {
            auto it = point_to_label.find(p);
            if(it != point_to_label.end()) {
                return it->second;
            }
            
            // Fallback: nearest neighbor search
            double min_dist = std::numeric_limits<double>::max();
            double label = std::numeric_limits<double>::quiet_NaN();
            
            for(const auto& kv : point_to_label) {
                double dx = p.x() - kv.first.x();
                double dy = p.y() - kv.first.y();
                double dz = p.z() - kv.first.z();
                double dist = dx*dx + dy*dy + dz*dz;
                
                if(dist < min_dist) {
                    min_dist = dist;
                    label = kv.second;
                }
            }
            
            return label;
        };
        
        // Add v1
        vertices.push_back(v1.x());
        vertices.push_back(v1.y());
        vertices.push_back(v1.z());
        vertex_labels.push_back(assign_label(v1));
        
        // Add v2
        vertices.push_back(v2.x());
        vertices.push_back(v2.y());
        vertices.push_back(v2.z());
        vertex_labels.push_back(assign_label(v2));
        
        // Add v3
        vertices.push_back(v3.x());
        vertices.push_back(v3.y());
        vertices.push_back(v3.z());
        vertex_labels.push_back(assign_label(v3));
    }
    
    // Convert to numpy arrays
    py::array_t<double> vertices_array({(size_t)vertices.size()/3, 3}, vertices.data());
    py::array_t<double> vertex_labels_array(vertex_labels.size(), vertex_labels.data());
    
    // Volume computation
    std::map<std::string, double> volume_data;
    if(volume) {
        double vol1 = 0.0;
        double vol2 = 0.0;
        std::list<Cell_handle> cells1;
        std::list<Cell_handle> cells2;
        
        as.get_alpha_shape_cells(std::back_inserter(cells1),
                                 Fixed_alpha_shape_3::EXTERIOR);
        as.get_alpha_shape_cells(std::back_inserter(cells2),
                                 Fixed_alpha_shape_3::INTERIOR);
        
        for(auto& cell : cells1) {
            Tetrahedron t(
                cell->vertex(0)->point(),
                cell->vertex(1)->point(),
                cell->vertex(2)->point(),
                cell->vertex(3)->point()
            );
            vol1 += std::abs(t.volume());
        }
        
        for(auto& cell : cells2) {
            Tetrahedron t(
                cell->vertex(0)->point(),
                cell->vertex(1)->point(),
                cell->vertex(2)->point(),
                cell->vertex(3)->point()
            );
            vol2 += std::abs(t.volume());
        }
        
        volume_data["exterior"] = vol1;
        volume_data["interior"] = vol2;
    }
    
    return std::make_tuple(vertices_array, vertex_labels_array, volume_data);
}

PYBIND11_MODULE(core, m) {
    m.doc() = "Fast 3D Alpha Hull with Label Propagation (C++ core)";
    m.def("fas_cpp_with_labels", &fas_cpp_with_labels, 
          "Compute alpha hull with label propagation",
          py::arg("points"), py::arg("alpha"), 
          py::arg("input_labels"), py::arg("volume") = false);
}