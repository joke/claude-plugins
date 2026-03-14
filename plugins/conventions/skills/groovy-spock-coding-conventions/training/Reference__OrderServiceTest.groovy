package com.github.joke.training.order

import org.apache.commons.collections4.ListUtils
import spock.lang.Specification
import spock.lang.Subject

class OrderServiceTest extends Specification {

    CustomerRepository customerRepository = Mock()

    @Subject(OrderService)
    final orderService = Spy(new OrderService(customerRepository))

    def 'get customers'() {
        SpyStatic(ListUtils)

        List<Customer> customers = Mock()
        List<Customer> unmodifiableCustomers = Mock()

        when:
        final res = orderService.customers

        then:
        1 * customerRepository.customers >> customers
        1 * ListUtils.unmodifiableList(customers) >> unmodifiableCustomers
        1 * orderService._
        0 * _

        expect:
        res == unmodifiableCustomers
    }

    def 'add customer'() {
        Customer customer = Mock()

        when:
        orderService.addCustomer(customer)

        then:
        1 * customerRepository.saveCustomer(customer)
        1 * orderService._
        0 * _
    }

    def 'find customer by name'() {
        Customer customer1 = Mock()
        Customer customer2 = Mock()

        when:
        final res = orderService.findCustomerByPrefix('some')

        then:
        1 * customerRepository.customers >> [customer1, customer2]
        1 * orderService.isCustomerWithMatchingName('some', customer1) >> true
        1 * orderService._
        0 * _

        expect:
        !res.empty
        res.get() == customer1
    }

    def 'throws bad customer exception from getBadCustomer'() {
        when:
        orderService.badCustomer

        then:
        1 * orderService._
        0 * _

        final ex = thrown BadCustomerException

        expect:
        ex.message == 'Bad customer'

    }
}
