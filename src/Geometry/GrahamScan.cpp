#ifndef GRAHAM_SCAN_CPP
#define GRAHAM_SCAN_CPP

#include "./Point.cpp"
#include <stdexcept>
#include <vector>
#include <algorithm>
#include <stack>

class GrahamScan {    
public:
    static Points computeConvexHull(Points points) {
        
        int points_size = points.size();
        if (points_size < 3) {
            throw std::invalid_argument("At least 3 points are required to compute the convex hull.");
        }

        int pivot_index = findPivotIndex(points);

        std::swap(points[0], points[pivot_index]);
        Point pivot = points[0];

        std::sort(
            points.begin() + 1,
            points.end(),
            [pivot](const Point& p1, const Point& p2) {
                return compare(pivot, p1, p2);
            }
        );
        
        std::stack<Point> hull;
        hull.push(points[0]);
        hull.push(points[1]);
        hull.push(points[2]);
        
        for (int i = 3; i < points_size; i++) {
            while (hull.size() > 1) {
                Point top = hull.top();
                hull.pop();
                Point nextToTop = hull.top();
                if (calculateOrientation(nextToTop, top, points[i]) != 2) continue;
                hull.push(top);
                break;
            }
            hull.push(points[i]);
        }

        Points convex_hull;
        while (!hull.empty()) {
            convex_hull.push_back(hull.top());
            hull.pop();
        }

        return convex_hull;
    }

private:
    static int findPivotIndex(const Points& points) {
        int min_y_index = 0;
        for (int i = 1; i < points.size(); i++) {
            if (
                points[i].getY() < points[min_y_index].getY()
                || (
                    points[i].getY() == points[min_y_index].getY()
                    && points[i].getX() < points[min_y_index].getX()
                )
            ) {
                min_y_index = i;
            }
        }
        return min_y_index;
    }

    static int calculateOrientation(const Point& p, const Point& q, const Point& r) {
        int val = (q.getY() - p.getY()) * (r.getX() - q.getX()) - (q.getX() - p.getX()) * (r.getY() - q.getY());
        if (val == 0) return 0;  // collinear
        return (val > 0) ? 1 : 2; // clock or counterclock wise
    }
    
    static double distanceSquared(const Point& p1, const Point& p2) {
        return (p1.getX() - p2.getX()) * (p1.getX() - p2.getX()) +
               (p1.getY() - p2.getY()) * (p1.getY() - p2.getY());
    }

    static bool compare(const Point &pivot, const Point& p1, const Point& p2) {
        int orientation = calculateOrientation(pivot, p1, p2);
        if (orientation == 0) {
            return distanceSquared(pivot, p2) >= distanceSquared(pivot, p1);
        }
        return (orientation == 2);
    }
};

#endif // GRAHAM_SCAN_CPP
