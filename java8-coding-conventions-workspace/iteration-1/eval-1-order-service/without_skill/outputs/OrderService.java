package com.example.service;

import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

public class OrderService {

    private final OrderRepository orderRepository;
    private final CustomerRepository customerRepository;

    public OrderService(final OrderRepository orderRepository, final CustomerRepository customerRepository) {
        this.orderRepository = orderRepository;
        this.customerRepository = customerRepository;
    }

    public List<Order> getActiveOrdersForCustomer(final String customerId) {
        final Customer customer = findCustomerOrThrow(customerId);
        final List<Order> allOrders = orderRepository.findByCustomerId(customer.getId());

        return allOrders.stream()
                .filter(this::isActive)
                .sorted(Comparator.comparing(Order::getCreatedDate))
                .collect(Collectors.toList());
    }

    public double calculateTotalRevenue(final List<Order> orders) {
        return orders.stream()
                .filter(this::isCompleted)
                .mapToDouble(this::calculateOrderRevenue)
                .sum();
    }

    public Optional<String> generateReport(final String customerId) {
        return findCustomer(customerId)
                .map(customer -> buildReport(customer, orderRepository.findByCustomerId(customerId)));
    }

    private String buildReport(final Customer customer, final List<Order> orders) {
        final long activeCount = countByStatus(orders, "ACTIVE");
        final long completedCount = countByStatus(orders, "COMPLETED");
        final double totalRevenue = calculateCompletedRevenue(orders);
        final String orderSummaries = formatOrderSummaries(orders);

        return String.format("Report for: %s%nActive orders: %d%nCompleted orders: %d%nTotal revenue: $%.1f%nOrders:%n%s",
                customer.getName(), activeCount, completedCount, totalRevenue, orderSummaries);
    }

    private long countByStatus(final List<Order> orders, final String status) {
        return orders.stream()
                .filter(order -> order.getStatus().equals(status))
                .count();
    }

    private double calculateCompletedRevenue(final List<Order> orders) {
        return orders.stream()
                .filter(this::isCompleted)
                .mapToDouble(Order::getPrice)
                .sum();
    }

    private String formatOrderSummaries(final List<Order> orders) {
        return orders.stream()
                .map(this::formatOrderSummary)
                .collect(Collectors.joining("\n"));
    }

    private String formatOrderSummary(final Order order) {
        return String.format("  - %s: %s ($%.1f)", order.getId(), order.getStatus(), order.getPrice());
    }

    private double calculateOrderRevenue(final Order order) {
        return (order.getPrice() - order.getDiscount()) + order.getTax();
    }

    private boolean isActive(final Order order) {
        return order.getStatus().equals("ACTIVE") && !order.isExpired();
    }

    private boolean isCompleted(final Order order) {
        return order.getStatus().equals("COMPLETED");
    }

    private Customer findCustomerOrThrow(final String customerId) {
        return findCustomer(customerId)
                .orElseThrow(() -> new CustomerNotFoundException(customerId));
    }

    private Optional<Customer> findCustomer(final String customerId) {
        return Optional.ofNullable(customerRepository.findById(customerId));
    }
}
