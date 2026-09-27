#ifndef POINT_H
#define POINT_H

#include <vector>

class Point {
public:
    Point(double x, double y) : x(x), y(y) {}
    double getX() const { return x; }
    double getY() const { return y; }
private:
    double x;
    double y;
};

typedef std::vector<Point> Points;

#endif // POINT_H