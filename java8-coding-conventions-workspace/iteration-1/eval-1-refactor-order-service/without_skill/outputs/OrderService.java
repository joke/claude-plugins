package com.example.service;

import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

public class OrderService {

    private static final String STATUS_ACTIVE = "ACTIVE";
    private static final String STATUS_COMPLETED = "COMPLETED";

    private final OrderRepository orderRepository;
    private final CustomerRepository customerRepository;

    public OrderService(OrderRepository orderRepository, CustomerRepository customerRepository) {
        this.orderRepository = orderRepository;
        this.customerRepository = customerRepository;
    }

    public Optional<Customer> findCustomer(String customerId) {
        return Optional.ofNullable(customerRepository.findById(customerId));
    }

    public List<Order> getActiveOrdersForCustomer(String customerId) {
        return findCustomer(customerId)
                .map(customer -> orderRepository.findByCustomerId(customerId).stream()
                        .filter(order -> STATUS_ACTIVE.equals(order.getStatus()))
                        .filter(order -> !order.isExpired())
                        .sorted(Comparator.comparing(Order::getCreatedDate))
                        .collect(Collectors.toList()))
                .orElseThrow(() -> new CustomerNotFoundException("Customer not found: " + customerId));
    }

    public double calculateTotalRevenue(List<Order> orders) {
        return orders.stream()
                .filter(order -> STATUS_COMPLETED.equals(order.getStatus()))
                .mapToDouble(this::calculateOrderTotal)
                .sum();
    }

    private double calculateOrderTotal(Order order) {
        return (order.getPrice() - order.getDiscount()) + order.getTax();
    }

    public String generateReport(String customerId) {
        return findCustomer(customerId)
                .map(customer -> buildReport(customer, orderRepository.findByCustomerId(customerId)))
                .orElse("Customer not found");
    }

    private String buildReport(Customer customer, List<Order> orders) {
        long activeCount = countByStatus(orders, STATUS_ACTIVE);
        long completedCount = countByStatus(orders, STATUS_COMPLETED);
        double totalRevenue = calculateCompletedRevenue(orders);
        String orderDetails = formatOrderSummaries(orders);

        return new StringBuilder()
                .append("Report for: ").append(customer.getName()).append("\n")
                .append("Active orders: ").append(activeCount).append("\n")
                .append("Completed orders: ").append(completedCount).append("\n")
                .append("Total revenue: $").append(totalRevenue).append("\n")
                .append("Orders:\n")
                .append(orderDetails)
                .toString();
    }

    private long countByStatus(List<Order> orders, String status) {
        return orders.stream()
                .filter(order -> status.equals(order.getStatus()))
                .count();
    }

    private double calculateCompletedRevenue(List<Order> orders) {
        return orders.stream()
                .filter(order -> STATUS_COMPLETED.equals(order.getStatus()))
                .mapToDouble(Order::getPrice)
                .sum();
    }

    private String formatOrderSummaries(List<Order> orders) {
        return orders.stream()
                .map(order -> String.format("  - %s: %s ($%s)", order.getId(), order.getStatus(), order.getPrice()))
                .collect(Collectors.joining("\n", "", "\n"));
    }
}
