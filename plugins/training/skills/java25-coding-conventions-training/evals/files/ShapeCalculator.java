package com.example.geometry;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class ShapeCalculator {

    public static abstract class Shape {
        public abstract String getType();
    }

    public static class Circle extends Shape {
        private final double radius;

        public Circle(double radius) {
            this.radius = radius;
        }

        public double getRadius() {
            return radius;
        }

        public String getType() {
            return "circle";
        }
    }

    public static class Rectangle extends Shape {
        private final double width;
        private final double height;

        public Rectangle(double width, double height) {
            this.width = width;
            this.height = height;
        }

        public double getWidth() {
            return width;
        }

        public double getHeight() {
            return height;
        }

        public String getType() {
            return "rectangle";
        }
    }

    public static class Triangle extends Shape {
        private final double base;
        private final double height;

        public Triangle(double base, double height) {
            this.base = base;
            this.height = height;
        }

        public double getBase() {
            return base;
        }

        public double getHeight() {
            return height;
        }

        public String getType() {
            return "triangle";
        }
    }

    public double calculateArea(Shape shape) {
        if (shape instanceof Circle) {
            Circle c = (Circle) shape;
            return Math.PI * c.getRadius() * c.getRadius();
        } else if (shape instanceof Rectangle) {
            Rectangle r = (Rectangle) shape;
            return r.getWidth() * r.getHeight();
        } else if (shape instanceof Triangle) {
            Triangle t = (Triangle) shape;
            return 0.5 * t.getBase() * t.getHeight();
        }
        throw new IllegalArgumentException("Unknown shape: " + shape.getClass().getName());
    }

    public String describe(Shape shape) {
        if (shape instanceof Circle) {
            Circle c = (Circle) shape;
            return "Circle with radius " + c.getRadius();
        } else if (shape instanceof Rectangle) {
            Rectangle r = (Rectangle) shape;
            return "Rectangle " + r.getWidth() + "x" + r.getHeight();
        } else if (shape instanceof Triangle) {
            Triangle t = (Triangle) shape;
            return "Triangle with base " + t.getBase() + " and height " + t.getHeight();
        }
        return "Unknown shape";
    }

    public List<Shape> filterByType(List<Shape> shapes, String type) {
        List<Shape> result = new ArrayList<>();
        for (Shape shape : shapes) {
            if (shape.getType().equals(type)) {
                result.add(shape);
            }
        }
        return Collections.unmodifiableList(result);
    }
}
