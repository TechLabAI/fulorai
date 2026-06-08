import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AsstFeatureAssetStudioComponent } from './asst-feature-asset-studio.component';

describe('AsstFeatureAssetStudioComponent', () => {
  let component: AsstFeatureAssetStudioComponent;
  let fixture: ComponentFixture<AsstFeatureAssetStudioComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AsstFeatureAssetStudioComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(AsstFeatureAssetStudioComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
