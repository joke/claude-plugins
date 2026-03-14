package com.github.joke.training.order;

import lombok.NoArgsConstructor;
import lombok.RequiredArgsConstructor;

import org.apache.commons.lang3.Strings;

import java.util.*;

import static lombok.AccessLevel.PRIVATE;
import static org.apache.commons.collections4.ListUtils.unmodifiableList;

//@Slf4j
@RequiredArgsConstructor
@NoArgsConstructor(access = PRIVATE, force = true)
public class OrderService {

    private final CustomerRepository customerRepository;

    public void addCustomer(Customer customer) {
        customerRepository.saveCustomer(customer);
    }

    public List<Customer> getCustomers() {
        return unmodifiableList(customerRepository.getCustomers());
    }

    public Optional<Customer> findCustomerByPrefix(String prefix) {
        return customerRepository.getCustomers().stream()
                .filter(customer -> isCustomerWithMatchingName(prefix, customer))
                .findFirst();
    }

    protected boolean isCustomerWithMatchingName(String name, Customer customer) {
        return Strings.CS.startsWith(name, customer.getName());
    }

    public boolean isBadCustomer() {
        throw new BadCustomerException("Bad customer");
    }
}
