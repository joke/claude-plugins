package com.example.geometry;

import static java.lang.Math.PI;

import java.util.List;

public class ShapeCalculator {

    public sealed interface Shape permits Circle, Rectangle, Triangle {
    }

    public record Circle(double radius) implements Shape {
    }

    public record Rectangle(double width, double height) implements Shape {
    }

    public record Triangle(double base, double height) implements Shape {
    }

    public static double calculateArea(final Shape shape) {
        return switch (shape) {
            case Circle c -> PI * c.radius() * c.radius();
            case Rectangle r -> r.width() * r.height();
            case Triangle t -> 0.5 * t.base() * t.height();
        };
    }

    public static String describe(final Shape shape) {
        return switch (shape) {
            case Circle c -> "Circle with radius " + c.radius();
            case Rectangle r -> "Rectangle " + r.width() + "x" + r.height();
            case Triangle t -> "Triangle with base " + t.base() + " and height " + t.height();
        };
    }

    public static <T extends Shape> List<T> filterByType(final List<Shape> shapes, final Class<T> type) {
        return shapes.stream()
                .filter(type::isInstance)
                .map(type::cast)
                .toList();
    }
}
