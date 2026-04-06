package com.example.service;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;

public class OrderService {

    private OrderRepository orderRepository;
    private CustomerRepository customerRepository;

    public OrderService(OrderRepository orderRepository, CustomerRepository customerRepository) {
        this.orderRepository = orderRepository;
        this.customerRepository = customerRepository;
    }

    public List<Order> getActiveOrdersForCustomer(String customerId) throws CustomerNotFoundException {
        Customer customer = customerRepository.findById(customerId);
        if (customer == null) {
            throw new CustomerNotFoundException("Customer not found: " + customerId);
        }

        List<Order> allOrders = orderRepository.findByCustomerId(customerId);
        List<Order> activeOrders = new ArrayList<>();
        for (Order order : allOrders) {
            if (order.getStatus().equals("ACTIVE") && !order.isExpired()) {
                activeOrders.add(order);
            }
        }

        // Sort by date
        for (int i = 0; i < activeOrders.size(); i++) {
            for (int j = i + 1; j < activeOrders.size(); j++) {
                if (activeOrders.get(i).getCreatedDate().after(activeOrders.get(j).getCreatedDate())) {
                    Order temp = activeOrders.get(i);
                    activeOrders.set(i, activeOrders.get(j));
                    activeOrders.set(j, temp);
                }
            }
        }

        return activeOrders;
    }

    public double calculateTotalRevenue(List<Order> orders) {
        double total = 0;
        for (Order order : orders) {
            if (order.getStatus().equals("COMPLETED")) {
                double price = order.getPrice();
                double discount = order.getDiscount();
                double tax = order.getTax();
                total += (price - discount) + tax;
            }
        }
        return total;
    }

    public String generateReport(String customerId) throws Exception {
        Customer customer = customerRepository.findById(customerId);
        if (customer == null) {
            return "Customer not found";
        }

        List<Order> orders = orderRepository.findByCustomerId(customerId);
        int activeCount = 0;
        int completedCount = 0;
        double totalRevenue = 0;
        List<String> orderSummaries = new ArrayList<>();

        for (Order order : orders) {
            if (order.getStatus().equals("ACTIVE")) {
                activeCount++;
            } else if (order.getStatus().equals("COMPLETED")) {
                completedCount++;
                totalRevenue += order.getPrice();
            }
            orderSummaries.add(order.getId() + ": " + order.getStatus() + " ($" + order.getPrice() + ")");
        }

        String report = "Report for: " + customer.getName() + "\n";
        report += "Active orders: " + activeCount + "\n";
        report += "Completed orders: " + completedCount + "\n";
        report += "Total revenue: $" + totalRevenue + "\n";
        report += "Orders:\n";
        for (String summary : orderSummaries) {
            report += "  - " + summary + "\n";
        }

        return report;
    }
}
