package com.github.joke.training.order;

import lombok.Data;
import org.apache.commons.lang3.Validate;

@Data
public class Customer {
    private final String id;
    private String name;
    private String email;
    private Address address;
    private CustomerType type;

    public void setName(String name) {
        Validate.notBlank(name);
        this.name = name;
    }

    public boolean isPremium() {
        return type == CustomerType.PREMIUM || type == CustomerType.VIP;
    }
}
