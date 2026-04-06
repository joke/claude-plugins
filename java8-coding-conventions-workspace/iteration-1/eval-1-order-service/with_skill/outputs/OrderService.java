package com.example.service;

import java.util.Comparator;
import java.util.List;
import java.util.Map;
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
        return filterActiveOrders(allOrders);
    }

    public double calculateTotalRevenue(final List<Order> orders) {
        return orders.stream()
                .filter(this::isCompleted)
                .mapToDouble(this::calculateOrderRevenue)
                .sum();
    }

    public String generateReport(final String customerId) {
        final Customer customer = findCustomerOrThrow(customerId);
        final List<Order> orders = orderRepository.findByCustomerId(customerId);
        final Map<Boolean, List<Order>> partitioned = partitionByCompleted(orders);
        final long activeCount = countByStatus(orders, "ACTIVE");
        final List<Order> completedOrders = partitioned.get(true);
        final double totalRevenue = calculateCompletedRevenue(completedOrders);
        final String orderDetails = formatOrderSummaries(orders);
        return formatReport(customer, activeCount, completedOrders.size(), totalRevenue, orderDetails);
    }

    private Customer findCustomerOrThrow(final String customerId) {
        return Optional.ofNullable(customerRepository.findById(customerId))
                .orElseThrow(() -> new CustomerNotFoundException(customerId));
    }

    private List<Order> filterActiveOrders(final List<Order> orders) {
        return orders.stream()
                .filter(this::isActiveAndNotExpired)
                .sorted(Comparator.comparing(Order::getCreatedDate))
                .collect(Collectors.toList());
    }

    private boolean isActiveAndNotExpired(final Order order) {
        return "ACTIVE".equals(order.getStatus()) && !order.isExpired();
    }

    private boolean isCompleted(final Order order) {
        return "COMPLETED".equals(order.getStatus());
    }

    private double calculateOrderRevenue(final Order order) {
        return (order.getPrice() - order.getDiscount()) + order.getTax();
    }

    private Map<Boolean, List<Order>> partitionByCompleted(final List<Order> orders) {
        return orders.stream()
                .collect(Collectors.partitioningBy(this::isCompleted));
    }

    private long countByStatus(final List<Order> orders, final String status) {
        return orders.stream()
                .filter(order -> status.equals(order.getStatus()))
                .count();
    }

    private double calculateCompletedRevenue(final List<Order> completedOrders) {
        return completedOrders.stream()
                .mapToDouble(Order::getPrice)
                .sum();
    }

    private static String formatOrderSummary(final Order order) {
        return order.getId() + ": " + order.getStatus() + " ($" + order.getPrice() + ")";
    }

    private static String formatOrderSummaries(final List<Order> orders) {
        return orders.stream()
                .map(OrderService::formatOrderSummary)
                .map(summary -> "  - " + summary)
                .collect(Collectors.joining("\n"));
    }

    private static String formatReport(final Customer customer,
                                       final long activeCount,
                                       final int completedCount,
                                       final double totalRevenue,
                                       final String orderDetails) {
        return "Report for: " + customer.getName() + "\n"
                + "Active orders: " + activeCount + "\n"
                + "Completed orders: " + completedCount + "\n"
                + "Total revenue: $" + totalRevenue + "\n"
                + "Orders:\n"
                + orderDetails + "\n";
    }
}
