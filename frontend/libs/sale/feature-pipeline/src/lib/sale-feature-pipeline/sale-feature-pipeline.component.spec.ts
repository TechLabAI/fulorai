import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SaleFeaturePipelineComponent } from './sale-feature-pipeline.component';

describe('SaleFeaturePipelineComponent', () => {
  let component: SaleFeaturePipelineComponent;
  let fixture: ComponentFixture<SaleFeaturePipelineComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SaleFeaturePipelineComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(SaleFeaturePipelineComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
