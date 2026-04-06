package com.example.service;

import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

public class OrderService {

    private static final String STATUS_ACTIVE = "ACTIVE";
    private static final String STATUS_COMPLETED = "COMPLETED";

    private final OrderRepository orderRepository;
    private final CustomerRepository customerRepository;

    public OrderService(final OrderRepository orderRepository, final CustomerRepository customerRepository) {
        this.orderRepository = orderRepository;
        this.customerRepository = customerRepository;
    }

    public List<Order> getActiveOrdersForCustomer(final String customerId) {
        final Customer customer = findCustomerOrThrow(customerId);
        final List<Order> allOrders = orderRepository.findByCustomerId(customerId);
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
        return formatReport(customer, orders);
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
        return order.getStatus().equals(STATUS_ACTIVE) && !order.isExpired();
    }

    private boolean isCompleted(final Order order) {
        return order.getStatus().equals(STATUS_COMPLETED);
    }

    private double calculateOrderRevenue(final Order order) {
        return (order.getPrice() - order.getDiscount()) + order.getTax();
    }

    private String formatReport(final Customer customer, final List<Order> orders) {
        final Map<Boolean, List<Order>> partitioned = orders.stream()
                .collect(Collectors.partitioningBy(this::isCompleted));
        final long activeCount = countByStatus(orders, STATUS_ACTIVE);
        final long completedCount = partitioned.get(true).size();
        final double totalRevenue = calculateCompletedRevenue(partitioned.get(true));
        final String orderDetails = formatOrderDetails(orders);

        return "Report for: " + customer.getName() + "\n"
                + "Active orders: " + activeCount + "\n"
                + "Completed orders: " + completedCount + "\n"
                + "Total revenue: $" + totalRevenue + "\n"
                + "Orders:\n"
                + orderDetails;
    }

    private long countByStatus(final List<Order> orders, final String status) {
        return orders.stream()
                .filter(order -> order.getStatus().equals(status))
                .count();
    }

    private double calculateCompletedRevenue(final List<Order> completedOrders) {
        return completedOrders.stream()
                .mapToDouble(Order::getPrice)
                .sum();
    }

    private String formatOrderDetails(final List<Order> orders) {
        return orders.stream()
                .map(this::formatOrderSummary)
                .collect(Collectors.joining());
    }

    private String formatOrderSummary(final Order order) {
        return "  - " + order.getId() + ": " + order.getStatus() + " ($" + order.getPrice() + ")\n";
    }
}
