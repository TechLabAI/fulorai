import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AsstFeatureAssetDetailComponent } from './asst-feature-asset-detail.component';

describe('AsstFeatureAssetDetailComponent', () => {
  let component: AsstFeatureAssetDetailComponent;
  let fixture: ComponentFixture<AsstFeatureAssetDetailComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AsstFeatureAssetDetailComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(AsstFeatureAssetDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
