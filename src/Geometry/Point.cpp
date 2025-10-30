#ifndef POINT_H
#define POINT_H

#include <vector>

typedef std::vector<Point> Points;

class Point {
public:
    Point(double x, double y) : x(x), y(y) {}
    double getX() const { return x; }
    double getY() const { return y; }
private:
    double x;
    double y;
};

#endif // POINT_H