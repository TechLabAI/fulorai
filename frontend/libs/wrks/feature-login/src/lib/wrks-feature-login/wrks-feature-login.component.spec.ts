import { ComponentFixture, TestBed } from '@angular/core/testing';
import { WrksFeatureLoginComponent } from './wrks-feature-login.component';

describe('WrksFeatureLoginComponent', () => {
  let component: WrksFeatureLoginComponent;
  let fixture: ComponentFixture<WrksFeatureLoginComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WrksFeatureLoginComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(WrksFeatureLoginComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
