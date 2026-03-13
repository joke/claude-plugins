package com.github.joke.training.order;

import lombok.RequiredArgsConstructor;
import lombok.Value;

import java.util.List;

import static java.util.Collections.unmodifiableList;

@RequiredArgsConstructor
public class CustomerRepository {
    List<Customer> customers;

    public List<Customer> getCustomers() {
        return unmodifiableList(customers);
    }

    public Customer saveCustomer(Customer customer) {
        customers.add(customer);
        return customer;
    }
}
