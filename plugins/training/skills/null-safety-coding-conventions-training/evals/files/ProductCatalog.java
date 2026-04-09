package com.example.catalog;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import javax.annotation.Nullable;

public class ProductCatalog {

    private final String catalogName;
    @Nullable
    private final String description;
    private final List<Product> products;
    @Nullable
    private final String promotionBanner;

    public ProductCatalog(final String catalogName, final String description,
                          final List<Product> products, final String promotionBanner) {
        this.catalogName = catalogName;
        this.description = description;
        this.products = Collections.unmodifiableList(products);
        this.promotionBanner = promotionBanner;
    }

    public String getCatalogName() {
        return catalogName;
    }

    public String getDescription() {
        return description;
    }

    public String getPromotionBanner() {
        return promotionBanner;
    }

    public String getDisplayHeader() {
        String header = catalogName;
        if (description != null) {
            header += " - " + description;
        }
        if (promotionBanner != null) {
            header += "\n" + promotionBanner;
        }
        return header;
    }

    public List<Product> getProducts() {
        return products;
    }

    public Product findByName(final String name) {
        for (final Product p : products) {
            if (p.getName().equals(name)) {
                return p;
            }
        }
        return null;
    }
}
