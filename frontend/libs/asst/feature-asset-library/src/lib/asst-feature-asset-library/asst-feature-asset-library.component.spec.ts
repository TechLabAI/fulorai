import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AsstFeatureAssetLibraryComponent } from './asst-feature-asset-library.component';

describe('AsstFeatureAssetLibraryComponent', () => {
  let component: AsstFeatureAssetLibraryComponent;
  let fixture: ComponentFixture<AsstFeatureAssetLibraryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AsstFeatureAssetLibraryComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(AsstFeatureAssetLibraryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
