package com.example.service;

public class CustomerNotFoundException extends RuntimeException {

    public CustomerNotFoundException(final String customerId) {
        super("Customer not found: " + customerId);
    }
}
