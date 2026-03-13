package com.github.joke.training.order;

public enum CustomerType {
    STANDARD(0.0),
    PREMIUM(0.10),
    VIP(0.20);

    private final double discountPercentage;

    CustomerType(double discountPercentage) {
        this.discountPercentage = discountPercentage;
    }

    public double getDiscountPercentage() {
        return discountPercentage;
    }
}
