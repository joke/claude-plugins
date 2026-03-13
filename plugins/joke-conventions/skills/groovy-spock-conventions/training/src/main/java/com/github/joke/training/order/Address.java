package com.github.joke.training.order;

import lombok.Value;

@Value
public class Address {
    String street;
    String city;
    String state;
    String zipCode;
    String country;

    public String getFullAddress() {
        return String.format("%s, %s, %s %s, %s", street, city, state, zipCode, country);
    }

}
