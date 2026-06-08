package com.journeyos.sale.infrastructure.persistence.adapter;

import com.journeyos.sale.application.port.out.ItemCompraRepositoryPort;
import com.journeyos.sale.domain.model.ItemCompra;
import com.journeyos.sale.infrastructure.persistence.repository.ItemCompraJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class ItemCompraRepositoryAdapter implements ItemCompraRepositoryPort {

    private final ItemCompraJpaRepository repository;

    @Override
    public ItemCompra save(ItemCompra entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<ItemCompra> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<ItemCompra> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
